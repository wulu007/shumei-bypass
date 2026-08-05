import os
from pathlib import Path

import pytest


@pytest.fixture
def resource_dir():
    _dir = Path(__file__).parent.parent / 'resources'
    os.makedirs(_dir, exist_ok=True)
    return _dir


@pytest.fixture
def test_org():
    return 'd6tpAY1oV0Kv5jRSgxQr'
