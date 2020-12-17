# Copyright (c) The Diem Core Contributors
# SPDX-License-Identifier: Apache-2.0

from .types.currency import CurrencyPairs, CurrencyPair
from .types.quote import Rate

fixed_rates = {
    str(CurrencyPairs.XUS_EUR.value): 926000,
    str(CurrencyPairs.XUS_USD.value): 1000000,
    str(CurrencyPairs.EUR_XUS.value): 1080000,
    str(CurrencyPairs.XUS_JPY.value): 107500000,
    str(CurrencyPairs.XUS_CHF.value): 980000,
    str(CurrencyPairs.GBP_XUS.value): 1230000,
    str(CurrencyPairs.XUS_CAD.value): 1410000,
    str(CurrencyPairs.AUD_XUS.value): 640000,
    str(CurrencyPairs.NZD_XUS.value): 600000,
}


def get_rate(currency_pair: CurrencyPair) -> Rate:
    try:
        return Rate(currency_pair, fixed_rates[str(currency_pair)])
    except KeyError:
        raise KeyError(f"LP does not support currency pair {currency_pair}")
