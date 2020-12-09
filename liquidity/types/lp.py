# Copyright (c) The Diem Core Contributors
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class LPDetails:
    sub_address: str
    vasp: str
    IBAN_number: str
