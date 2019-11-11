import pytest
import requests
import sqlite3
from classes.Movie import Movie
from classes.DB import DB


class MockResponse_OK:
    @staticmethod
    def json(file='fixtures/alien.json'):
        import json
        with open(file, 'r') as read_file:
            data = json.load(read_file)
        return data


class MockResponse_NO_PARAMS:
    @staticmethod
    def json():
        return {"Response": "False", "Error": "Something went wrong."}


class MockDB:
    def __init__(self):
        self.conn = sqlite3.connect('test.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS movies (ID INTEGER PRIMARY KEY, \
            TITLE TEXT, YEAR INTEGER,  RUNTIME TEXT, GENRE TEXT, \
            DIRECTOR TEXT, CAST TEXT, WRITER TEXT, LANGUAGE TEXT, \
            COUNTRY TEXT, AWARDS TEXT, IMDb_Rating FLOAT, \
            IMDb_votes INTEGER, BOX_OFFICE INTEGER)"
        )


class MockDBPopulated:
    def __init__(self):
        self.conn = sqlite3.connect('populated.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS movies (ID INTEGER PRIMARY KEY, \
            TITLE TEXT, YEAR INTEGER,  RUNTIME TEXT, GENRE TEXT, \
            DIRECTOR TEXT, CAST TEXT, WRITER TEXT, LANGUAGE TEXT, \
            COUNTRY TEXT, AWARDS TEXT, IMDb_Rating FLOAT, \
            IMDb_votes INTEGER, BOX_OFFICE INTEGER)"
        )
        alien = Movie.json_to_movie(
            MockResponse_OK().json()
            )
        boyhood = Movie.json_to_movie(
            MockResponse_OK().json('fixtures/boyhood.json')
            )
        forrest = Movie.json_to_movie(
            MockResponse_OK().json('fixtures/forrest.json')
            )
        memento = Movie.json_to_movie(
            MockResponse_OK().json('fixtures/memento.json')
            )
        shawshank = Movie.json_to_movie(
            MockResponse_OK().json('fixtures/shawshank.json')
            )
        DB.insert(self, "Alien")
        DB.update(self, alien)
        DB.insert(self, "Boyhood")
        DB.update(self, boyhood)
        DB.insert(self, "Forrest Gump")
        DB.update(self, forrest)
        DB.insert(self, "Memento")
        DB.update(self, memento)
        DB.insert(self, "The Shawshank Redemption")
        DB.update(self, shawshank)


@pytest.fixture
def mock_response(monkeypatch, auth):
    def mock_get(*args, **kwargs):
        return MockResponse_OK() if {"t": "Alien", "apikey": auth} \
            in args else MockResponse_NO_PARAMS()

    monkeypatch.setattr(requests, 'get', mock_get)


@pytest.fixture
def auth():
    import json
    with open('apikey.json', 'r') as f:
        auth = json.load(f)
    return auth


@pytest.fixture()
def mock_db():
    return MockDB()


@pytest.fixture()
def mock_db_ok():
    return MockResponse_OK()


@pytest.fixture()
def mock_db_populated():
    return MockDBPopulated()
