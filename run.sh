#!/bin/bash

# Copyright (c) The Diem Core Contributors
# SPDX-License-Identifier: Apache-2.0

export ACCOUNT_WATCH=${ACCOUNT_WATCHER_AUTH_KEY:-false}
if [ $ACCOUNT_WATCH != 'false' ]; then
  echo "Starting the account watcher..."
  # Run Python with unbuffered stdout (-u flag) to see the logs properly
  python -u /liquidity/account_watcher.py &
fi

export FLASK_ENV=${COMPOSE_ENV:-development}
export FLASK_APP="webapp:init()"
pipenv run flask run --no-reload --host 0.0.0.0 --port ${LIQUIDITY_PORT:-5000}
