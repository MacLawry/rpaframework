import copy
import io
import json
import pytest
from RPA.core.locators import (
    TYPES,
    LocatorsDatabase,
    Locator,
    BrowserDOM,
    ImageTemplate,
)


LEGACY = [
    {
        "id": 0,
        "name": "RobotSpareBin.Username",
        "type": "browser",
        "strategy": "id",
        "value": "username",
        "source": "https://robotsparebinindustries.com/",
    },
    {
        "id": 1,
        "name": "RobotSpareBin.Password",
        "type": "browser",
        "strategy": "id",
        "value": "password",
        "source": "https://robotsparebinindustries.com/",
    },
    {
        "id": 2,
        "name": "RobotSpareBin.Login",
        "type": "browser",
        "strategy": "class",
        "value": "btn-primary",
        "source": "https://robotsparebinindustries.com/",
    },
]

CURRENT = {
    "RobotSpareBin.Username": {
        "type": "browser",
        "strategy": "id",
        "value": "username",
        "source": "https://robotsparebinindustries.com/",
    },
    "RobotSpareBin.Password": {
        "type": "browser",
        "strategy": "id",
        "value": "password",
        "source": "https://robotsparebinindustries.com/",
    },
    "RobotSpareBin.Login": {
        "type": "browser",
        "strategy": "class",
        "value": "btn-primary",
        "source": "https://robotsparebinindustries.com/",
    },
}


def to_stream(data):
    return io.StringIO(json.dumps(data))


class TestLocators:
    def test_types(self):
        assert "browser" in TYPES
        assert "image" in TYPES

    def test_from_dict(self):
        data = {
            "type": "browser",
            "strategy": "class",
            "value": "btn-primary",
            "source": "https://robotsparebinindustries.com/",
        }

        locator = Locator.from_dict(data)
        assert isinstance(locator, BrowserDOM)
        assert locator.strategy == "class"
        assert locator.value == "btn-primary"
        assert locator.source == "https://robotsparebinindustries.com/"

    def test_from_dict_extras(self):
        data = {
            "type": "browser",
            "strategy": "class",
            "value": "btn-primary",
            "source": "https://robotsparebinindustries.com/",
            "notvalid": "somevalue",
        }

        locator = Locator.from_dict(data)
        assert isinstance(locator, BrowserDOM)

    def test_from_dict_optional(self):
        data = {
            "type": "browser",
            "strategy": "class",
            "value": "btn-primary",
        }

        locator = Locator.from_dict(data)
        assert isinstance(locator, BrowserDOM)
        assert locator.strategy == "class"
        assert locator.value == "btn-primary"
        assert locator.source == None

    def test_from_dict_required(self):
        data = {
            "type": "browser",
            "strategy": "class",
        }

        with pytest.raises(ValueError):
            Locator.from_dict(data)

    def test_from_dict_no_type(self):
        data = {
            "strategy": "class",
            "value": "btn-primary",
        }

        with pytest.raises(ValueError):
            Locator.from_dict(data)


class TestDatabase:
    @pytest.fixture
    def legacy_database(self):
        database = LocatorsDatabase(to_stream(LEGACY))
        database.load()
        return database

    @pytest.fixture
    def current_database(self):
        database = LocatorsDatabase(to_stream(CURRENT))
        database.load()
        return database

    def test_load_legacy(self):
        database = LocatorsDatabase(to_stream(LEGACY))
        database.load()

        assert database.error is None
        assert len(database.locators) == 3

    def test_load_legacy_empty(self):
        database = LocatorsDatabase(to_stream({}))
        database.load()

        assert database.error is None
        assert len(database.locators) == 0

    def test_legacy_missing_name(self):
        content = copy.deepcopy(LEGACY)
        del content[1]["name"]

        database = LocatorsDatabase(to_stream(content))
        database.load()

        assert database.error is None
        assert len(database.locators) == 2

    def test_load_malformed(self):
        stream = io.StringIO("not-a-json{]}\\''")

        database = LocatorsDatabase(stream)
        database.load()

        assert database.error is not None
        assert len(database.error) == 2
        assert len(database.locators) == 0

    def test_load_missing(self):
        database = LocatorsDatabase("not/a/valid/path")
        database.load()

        assert database.error is None
        assert len(database.locators) == 0

    def test_reset_error(self):
        database = LocatorsDatabase()

        database.path = io.StringIO("some-error")
        database.load()

        assert database.error is not None
        assert len(database.locators) == 0

        database.path = to_stream(LEGACY)
        database.load()

        assert database.error is None
        assert len(database.locators) == 3
