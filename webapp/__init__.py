# pyre-strict

# Copyright (c) The Diem Core Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import logging
from uuid import UUID

from flask import Flask, request
from flask.logging import default_handler

from liquidity import init_liquidity_provider
from liquidity.storage import Session
from .api import api
from .errors import errors

root = logging.getLogger()
root.setLevel(logging.DEBUG)
root.addHandler(default_handler)


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def _create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(errors)
    app.register_blueprint(api)
    app.json_encoder = UUIDEncoder
    app.debug = True
    return app


app: Flask = _create_app()


def init() -> Flask:
    print("starting init liquidity")
    # make sure to run the LP init only once, even when in debug mode
    with app.app_context():
        init_liquidity_provider(app.logger)

    return app


@app.before_request
def log_request_info():
    app.logger.debug("Body: %s", repr(request.get_data()))


@app.teardown_appcontext
def remove_session(*args, **kwargs) -> None:  # pyre-ignore
    Session.remove()
