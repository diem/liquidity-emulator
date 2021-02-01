# Liquidity Service Emulator

## Development

This project used the following tools:

- Flask as the HTTP server.
- Black for automatic code formatting.
- Flake8 for linting.

### Testnet setup

```shell script
pipenv install --dev
pipenv run pre-commit install
pipenv run python setup_env.py
./run.sh
```

The last command will install the git hooks that will run code formatting
and linting on each commit.

### Premainnet setup

Premainnet setup works identically to the testnet setup, but requires two
environment variables to be present: `BLOCKCHAIN` and `LIQUIDITY_ACCOUNT_PRIVATE_KEY`.

The value of `BLOCKCHAIN` must be `premainnet`; the value of
`LIQUIDITY_ACCOUNT_PRIVATE_KEY` must be the private key of the Designated
Dealer account, encoded as a hexadecimal string.


### PyCharm configuration
- Add Black to `Settings/Tools/File Watchers` as described in the [documentation][1].

### Helper scripts
- `run.sh` Starts the HTTP server
- `develop.sh` Starts the HTTP server with code auto-reloading.
- `lint.sh` Fix code formatting and run linting


[1]: https://black.readthedocs.io/en/stable/editor_integration.html
