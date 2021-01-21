# Liquidity Service Emulator

## Development

This project used the following tools:

- Flask as the HTTP server.
- Black for automatic code formatting.
- Flake8 for linting.

### Setup

```shell script
pipenv install --dev
pipenv run pre-commit install
pipenv run python setup_env.py
./run.sh
```

The last command will install the git hooks that will run code formatting
and linting on each commit.

### PyCharm configuration
- Add Black to `Settings/Tools/File Watchers` as described in the [documentation][1].

### Helper scripts
- `run.sh` Starts the HTTP server
- `develop.sh` Starts the HTTP server with code auto-reloading.
- `lint.sh` Fix code formatting and run linting


[1]: https://black.readthedocs.io/en/stable/editor_integration.html
