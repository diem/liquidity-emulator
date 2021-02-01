import json
import logging
import os

from diem import testnet, LocalAccount, jsonrpc

liquidity_account_name = "liquidity"

PREMAINNET_CHAIN_ID = int(os.getenv("PREMAINNET_CHAIN_ID", "21"))

ENV_FILE_NAME = os.getenv("ENV_FILE_NAME", ".env")


def to_compact_json(d: dict) -> str:
    return json.dumps(d, separators=(",", ":"))


if __name__ == "__main__":
    chain = os.getenv("BLOCKCHAIN", "testnet")

    if chain == "premainnet":
        print(f"Configuring for premainnet (chain ID: {PREMAINNET_CHAIN_ID})")

        vasp_private_key = os.environ["LIQUIDITY_ACCOUNT_PRIVATE_KEY"]
        account = LocalAccount.from_private_key_hex(vasp_private_key)

        json_rpc_url = "https://premainnet.diem.com/v1"
        jsonrpc_client = jsonrpc.Client(json_rpc_url)
        jsonrpc_client.must_get_account(account.account_address)
        print("Premainnet account is valid")

        lp_custody_private_keys = to_compact_json(
            {liquidity_account_name: vasp_private_key}
        )

        print(f"Creating {ENV_FILE_NAME} file")
        with open(ENV_FILE_NAME, "w") as dotenv:
            dotenv.write(f"LIQUIDITY_CUSTODY_ACCOUNT_NAME={liquidity_account_name}\n")
            dotenv.write(f"CUSTODY_PRIVATE_KEYS={lp_custody_private_keys}\n")
            dotenv.write(f"LIQUIDITY_VASP_ADDR={account.account_address.to_hex()}\n")
            dotenv.write(f"JSON_RPC_URL={json_rpc_url}\n")
            dotenv.write(f"CHAIN_ID={PREMAINNET_CHAIN_ID}\n")
    elif chain == "testnet":
        print("Configuring for testnet")
        print(f"Creating {ENV_FILE_NAME} file")
        with open(ENV_FILE_NAME, "w") as dotenv:
            dotenv.write(f"JSON_RPC_URL=https://testnet.diem.com/v1\n")
            dotenv.write(f"CHAIN_ID={testnet.CHAIN_ID.value}\n")
    else:
        logging.error(f"Unknown blockchain type {chain}")
        exit(1)
