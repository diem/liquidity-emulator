from diem import chain_ids

from liquidity import create_liquidity_provider, init_liquidity_provider
from liquidity.liquidity import FaucetLiquidityProvider, DDLiquidityProvider

CUSTODY_PRIVATE_KEYS = (
    '{"liquidity":"c6537e56d844fa4a15f3bf5eacd41c9123a19ef19a1026f2325a6b2dd33a13f1"}'
)


def test_faucet_liquidity_provider_factory_for_testnet_without_custody_private_keys(
    patch_liquidity, monkeypatch
) -> None:
    monkeypatch.setenv("CHAIN_ID", str(chain_ids.TESTNET.value))
    monkeypatch.delenv("CUSTODY_PRIVATE_KEYS", raising=False)

    init_liquidity_provider()
    lp = create_liquidity_provider()
    assert isinstance(lp, FaucetLiquidityProvider)


def test_dd_liquidity_provider_factory_for_testnet_with_custody_private_keys(
    patch_liquidity, monkeypatch
) -> None:
    monkeypatch.setenv("CHAIN_ID", str(chain_ids.TESTNET.value))
    monkeypatch.setenv("CUSTODY_PRIVATE_KEYS", CUSTODY_PRIVATE_KEYS)

    init_liquidity_provider()
    lp = create_liquidity_provider()
    assert isinstance(lp, DDLiquidityProvider)


def test_dd_liquidity_provider_factory_for_premainnet(
    patch_liquidity, monkeypatch
) -> None:
    monkeypatch.setenv("CHAIN_ID", str(chain_ids.PREMAINNET.value))
    monkeypatch.setenv("CUSTODY_PRIVATE_KEYS", CUSTODY_PRIVATE_KEYS)

    init_liquidity_provider()
    lp = create_liquidity_provider()
    assert isinstance(lp, DDLiquidityProvider)
