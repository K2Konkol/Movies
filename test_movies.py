import pytest
import requests
import movies
import sqlite3
from movies import DB

FAKE_URL = 'http://fake_url'


class MockResponse_OK:
    @staticmethod
    def json():
        import json
        with open('alien.json', 'r') as read_file:
            data = json.load(read_file)
        return data


class MockResponse_NO_PARAMS:
    @staticmethod
    def json():
        return {"Response":"False","Error":"Something went wrong."}
        # return {"Response":"False","Error":"No API key provided."}
        # return {"Response":"False","Error":"Movie not found!"}

class MockDB:
    def __init__(self):
        self.conn = sqlite3.connect('test.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS movies (ID INTEGER PRIMARY KEY, TITLE TEXT, YEAR INTEGER,  RUNTIME TEXT, GENRE TEXT, DIRECTOR TEXT, CAST TEXT, WRITER TEXT, LANGUAGE TEXT, COUNTRY TEXT, AWARDS TEXT, IMDb_Rating FLOAT, IMDb_votes INTEGER, BOX_OFFICE INTEGER)")


@pytest.fixture
def mock_response(monkeypatch):

    def mock_get(*args, **kwargs):
        return MockResponse_OK() if {"t":"Alien","apikey":auth} in args else MockResponse_NO_PARAMS()

    monkeypatch.setattr(requests, 'get', mock_get)

@pytest.fixture
def auth():
    import json
    with open('apikey.json', 'r') as f:
        auth = json.load(f)
    return auth

@pytest.fixture(scope="session")
def mock_db():
    return MockDB()


def test_get_movie_no_apikey(mock_response):
    """Test that function returns an error if no API key is provided"""
    result = movies.get_movie(FAKE_URL, params=None)
    assert 'Error' in result

def test_get_movie_no_title(mock_response):
    """Test that function returns an error if no movie title is provided"""
    result = movies.get_movie(FAKE_URL, params=auth)
    assert 'Error' in result

def test_get_movie(mock_response):
    """Test that function returns JSON if both API key and movie title are provided"""
    params={"t":"Alien","apikey":auth}
    result = movies.get_movie(FAKE_URL, params=params)
    assert 'Alien' in result['Title']

def test_get_apikey(auth):
    """Test that function returns apikey"""
    assert movies.get_apikey() == auth 

def test_parse_awards_no_oscar():
    data = "3 wins & 1 nomination."
    assert movies.parse_awards(data) == {"oscars_won":'N/A', "oscar_nominations":'N/A', "another_wins":"3", "another_nominations":"1"}

def test_parse_awards_oscar_nominated():
    data = "Nominated for 7 Oscars. Another 19 wins & 32 nominations."
    assert movies.parse_awards(data) == {"oscars_won":'N/A', "oscar_nominations":'7', "another_wins":'19', "another_nominations":'32'}

def test_parse_awards_oscar_won():
    data = "Won 1 Oscar. Another 16 wins & 19 nominations."
    assert movies.parse_awards(data) == {"oscars_won":'1', "oscar_nominations":'N/A', "another_wins":'16', "another_nominations":'19'}

def test_parse_json_to_movie(monkeypatch):
    response = MockResponse_OK().json()
    alien = movies.json_to_movie(response)
    assert alien.title == 'Alien'
    assert alien.director == 'Ridley Scott'
    assert alien.cast == 'Tom Skerritt, Sigourney Weaver, Veronica Cartwright, Harry Dean Stanton'
    assert alien.awards == 'Won 1 Oscar. Another 16 wins & 19 nominations.'

def test_db_empty(mock_db):
    db = DB.get_all_titles(mock_db)
    assert len(db.fetchall()) == 0

def test_insert_not_duplicated(mock_db):
    title = {"Title":"Alien"}
    DB.insert(mock_db, title)
    DB.insert(mock_db, title)
    db = DB.get_all_titles(mock_db)
    items = db.fetchall()
    assert len(items) == 1
    assert 'Alien' in str(items)

def test_update(monkeypatch, mock_db):
    alien = MockResponse_OK().json()
    DB.insert(mock_db, alien)
    DB.update(mock_db, alien)
    db = DB.get_by_title(mock_db, alien)
    item = db.fetchone()
    assert 'Alien' in str(item)
    assert 'Won 1 Oscar. Another 16 wins & 19 nominations.' in str(item)
    assert '8.4' in str(item)