from datetime import datetime, timedelta

import pytest
from diem import LocalAccount
from diem.jsonrpc import Account

from liquidity.storage import Quote, Trade
from liquidity.custody import Custody
from liquidity.types.currency import CurrencyPairs
from liquidity.types.quote import QuoteId

from liquidity import liquidity


class CustodyMock:
    def get_account(
        self, account_name: str = "test_default_account_name"
    ) -> LocalAccount:
        local_account = LocalAccount.generate()

        return local_account


class LiquidityProviderMock:
    @staticmethod
    def find_quote(quote_id: QuoteId) -> Quote:
        return Quote(
            id=str(quote_id),
            currency_pair=CurrencyPairs.Coin1_USD,
            rate=1000000,
            amount=10000000,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(minutes=10),
        )

    @staticmethod
    def create_trade(direction, quote_id: QuoteId):
        return Trade(
            direction=direction,
            quote_id=str(quote_id),
        )

    @staticmethod
    def fetch_account_info():
        return Account(sequence_number=3)


@pytest.fixture(scope="function")
def patch_liquidity(monkeypatch):
    monkeypatch.setattr(Custody, "get_account", CustodyMock.get_account)
    monkeypatch.setattr(liquidity, "find_quote", LiquidityProviderMock.find_quote)
    monkeypatch.setattr(liquidity, "create_trade", LiquidityProviderMock.create_trade)
