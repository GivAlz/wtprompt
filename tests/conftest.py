import os

import pytest

@pytest.fixture
def test_folder_location():
    return os.path.dirname(os.path.abspath(__file__))
