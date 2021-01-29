# pyre-ignore-all-errors[6]

# Copyright (c) The Diem Core Contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import secrets
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional

from diem import identifier, utils, jsonrpc, diem_types, serde_types, testnet, chain_ids
from diem.testnet import DESIGNATED_DEALER_ADDRESS

from .custody import Custody
from .types.currency import CurrencyPairs, CurrencyPair
from .types.errors import TradeError
from .types.lp import LPDetails
from .types.quote import QuoteData, QuoteId, Rate
from .types.settlement import DebtData, DebtId
from .types.trade import Direction, TradeId, TradeData
from .vasp import Vasp
from . import storage
from .fx import get_rate
from .storage import (
    create_quote,
    create_trade,
    find_trade,
    find_quote,
    create_new_settlement,
    get_all_unsettled_debts,
    settle_debt,
)

LP_IBAN_ADDRESS = "US89 3704 0044 0532 0130 00"

logger = logging.getLogger(__name__)


class LiquidityProvider(ABC):
    def __init__(self, address_str: str):
        self.address_str = address_str

    @abstractmethod
    def _trade_and_execute_buy(
        self,
        quote,
        trade,
        diem_deposit_address,
    ):
        pass

    def _trade_and_execute_sell(self, trade, tx_version):
        # Here liquidity provider will validate tx_version supplied by
        # the user match the trade currency and amount.
        trade.executed(tx_version)

    def lp_details(self) -> LPDetails:
        """
        Liquidity provider details including:
          - LP settlement diem blockchain address
          - LP settlement bank account ISBN
          - Supported Currency pairs
        """
        return LPDetails(
            sub_address=secrets.token_hex(identifier.DIEM_SUBADDRESS_SIZE),
            vasp=self.address_str,
            IBAN_number=LP_IBAN_ADDRESS,
        )

    def get_quote(self, pair: CurrencyPair, amount: int) -> QuoteData:
        """
        Get a buy & sell quote for the given currency pair and amount.
        i.e DiemUsd/USD will return the rate that you BUY / SELL
        1 DiemUsd in exchange for USD at some conversion rate.
        :param pair:
        :param amount:
        :return: quote with buy & sell
        """
        storage_quote = create_quote(
            currency_pair=CurrencyPairs.from_pair(pair),
            rate=get_rate(currency_pair=pair).rate,
            amount=amount,
            expires_at=datetime.now() + timedelta(minutes=10),
        )

        return QuoteData(
            quote_id=QuoteId(uuid.UUID(storage_quote.id)),
            rate=Rate(storage_quote.currency_pair.value, storage_quote.rate),
            expires_at=storage_quote.expires_at,
            amount=storage_quote.amount,
        )

    def trade_info(self, trade_id: TradeId) -> TradeData:
        """
        Returns trade execution status for a given trade.
        :param trade_id:
        :return:
        """
        trade = find_trade(trade_id)

        return TradeData(
            trade_id=TradeId(uuid.UUID(trade.id)),
            direction=trade.direction,
            pair=trade.quote.currency_pair.value,
            amount=trade.quote.amount,
            quote=QuoteData(
                quote_id=QuoteId(uuid.UUID(trade.quote.id)),
                rate=Rate(trade.quote.currency_pair.value, trade.quote.rate),
                expires_at=trade.quote.expires_at,
                amount=trade.quote.amount,
            ),
            status=trade.status,
            tx_version=trade.tx_version,
        )

    def get_debt(self) -> List[DebtData]:
        """
        Start a Fiat settlement process.
        :return:
        """
        create_new_settlement()
        unsettled = get_all_unsettled_debts()

        return [
            DebtData(
                debt_id=DebtId(uuid.UUID(debt.id)),
                currency=debt.currency,
                amount=debt.amount,
            )
            for debt in unsettled
        ]

    def settle(self, debt_id: DebtId, settlement_confirmation: str):
        """
        Confirm debt payment.
        """
        settle_debt(debt_id, settlement_confirmation)

    def trade_and_execute(
        self,
        quote_id: QuoteId,
        direction: Direction,
        diem_bech32_deposit_address: Optional[str] = None,
        tx_version: Optional[int] = None,
    ) -> TradeId:
        """
        For simplicity trade and execute steps embodied into one action.
        On Trade LP will update it's internal ledger with new state of
        balances according to the wallet trade request; i.e For buy trade
        of 1 DiemUsd for 1 Usd wallet balance on LP side will update
        wallet balance to be+1 DiemUSD -1 USD.

        On execution of such trade +1 DiemUSD will be transferred to
        diem_deposit_address so new balance on LP side is now 0 DiemUSD
        -1 USD. Fiat debt is settled in a separate call
        :param quote_id:
        :param direction: BUY / SELL
        :param diem_bech32_deposit_address: Your Diem wallet address for the deposit
        :param tx_version: Transaction version for the deposit you made
                           into LP Diem wallet address; i.e for a buy
                           trade of DiemUSD/Diem you will have to send
                           Diem to the LP deposit address you obtained
                           from lp_details() call
        :return:
        """
        quote = find_quote(quote_id)
        trade = create_trade(direction, quote_id)

        if Direction[trade.direction] == Direction.Buy:
            self._trade_and_execute_buy(
                quote=quote,
                trade=trade,
                diem_deposit_address=diem_bech32_deposit_address,
            )
        elif Direction[trade.direction] == Direction.Sell:
            self._trade_and_execute_sell(trade, tx_version)
        else:
            raise AssertionError("Trade direction have to be either Buy or Sell.")

        return TradeId(uuid.UUID(trade.id))


class DDLiquidityProvider(LiquidityProvider):
    def __init__(self):
        liquidity_custody_account_name = os.getenv(
            "LIQUIDITY_CUSTODY_ACCOUNT_NAME", "liquidity"
        )
        self.chain_id = int(os.environ["CHAIN_ID"])
        self.vasp = Vasp(
            jsonrpc.Client(os.environ["JSON_RPC_URL"]), liquidity_custody_account_name
        )

        super().__init__(self.vasp.address_str)

    def _trade_and_execute_buy(self, quote, trade, diem_deposit_address):
        if not diem_deposit_address:
            raise TradeError("Can't execute trade without a deposit address")

        receiver_vasp, receiver_sub_address = identifier.decode_account(
            diem_deposit_address, identifier.HRPS.get(self.chain_id, identifier.PDM)
        )

        tx_version, tx_sequence = self.vasp.send_transaction(
            currency=quote.currency_pair.value.base,
            amount=quote.amount,
            dest_vasp_address=utils.account_address_hex(receiver_vasp),
            dest_sub_address=receiver_sub_address.hex(),
        )

        trade.executed(tx_version)


class FaucetLiquidityProvider(LiquidityProvider):
    def __init__(self):
        super().__init__(utils.account_address_hex(DESIGNATED_DEALER_ADDRESS))

    def _trade_and_execute_buy(self, quote, trade, diem_deposit_address):
        if not diem_deposit_address:
            raise TradeError("Can't execute trade without a deposit address")

        receiver_vasp, receiver_sub_address = identifier.decode_account(
            diem_deposit_address, identifier.HRPS[testnet.CHAIN_ID.to_int()]
        )

        client = testnet.create_client()

        account = client.get_account(receiver_vasp)

        faucet = testnet.Faucet(client)
        faucet.mint(
            account.authentication_key, quote.amount, quote.currency_pair.value.base
        )


def liquidity_provider_default_factory() -> LiquidityProvider:
    raise EnvironmentError("Cannot create a liquidity provider before init")


_liquidity_provider_factory = liquidity_provider_default_factory


def create_liquidity_provider() -> LiquidityProvider:
    return _liquidity_provider_factory()


def init_liquidity_provider(app_logger=None):
    global logger
    if app_logger:
        logger = app_logger

    logger.info("Configure and create storage")
    storage.configure_storage()
    storage.create_storage()

    chain_id = diem_types.ChainId(value=serde_types.uint8(os.environ["CHAIN_ID"]))
    custody_private_keys = os.getenv("CUSTODY_PRIVATE_KEYS")

    global _liquidity_provider_factory
    if chain_id == chain_ids.TESTNET and custody_private_keys is None:
        _liquidity_provider_factory = FaucetLiquidityProvider
    else:
        logger.info("Custody init")
        Custody.init(chain_id)
        _liquidity_provider_factory = DDLiquidityProvider
