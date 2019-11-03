import pytest
import requests
import movies
import sqlite3
from movies import DB

FAKE_URL = 'http://fake_url'


class MockResponse_OK:
    @staticmethod
    def json(file='alien.json'):
        import json
        with open(file, 'r') as read_file:
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


class MockDBPopulated:
    def __init__(self):
        self.conn = sqlite3.connect('populated.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS movies (ID INTEGER PRIMARY KEY, TITLE TEXT, YEAR INTEGER,  RUNTIME TEXT, GENRE TEXT, DIRECTOR TEXT, CAST TEXT, WRITER TEXT, LANGUAGE TEXT, COUNTRY TEXT, AWARDS TEXT, IMDb_Rating FLOAT, IMDb_votes INTEGER, BOX_OFFICE INTEGER)")
        alien = movies.json_to_movie(MockResponse_OK().json())
        boyhood = movies.json_to_movie(MockResponse_OK().json('boyhood.json'))
        forrest = movies.json_to_movie(MockResponse_OK().json('forrest.json'))
        memento = movies.json_to_movie(MockResponse_OK().json('memento.json'))
        shawshank = movies.json_to_movie(MockResponse_OK().json('shawshank.json'))    
        DB.insert(self, alien)
        DB.update(self, alien)
        DB.insert(self, boyhood)
        DB.update(self, boyhood)
        DB.insert(self, forrest)
        DB.update(self, forrest)
        DB.insert(self, memento)
        DB.update(self, memento)
        DB.insert(self, shawshank)
        DB.update(self, shawshank)


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

@pytest.fixture()
def mock_db():
    return MockDB()

@pytest.fixture()
def mock_db_populated():
    return MockDBPopulated()

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
    assert alien.Title == 'Alien'
    assert alien.Director == 'Ridley Scott'
    assert alien.Cast == 'Tom Skerritt, Sigourney Weaver, Veronica Cartwright, Harry Dean Stanton'
    assert alien.Awards == 'Won 1 Oscar. Another 16 wins & 19 nominations.'

def test_db_empty(mock_db):
    db = DB.get_all_titles(mock_db)
    assert len(db.fetchall()) == 0

def test_insert_not_duplicated(mock_db):
    title = movies.Movie(Title='Alien')
    DB.insert(mock_db, title)
    DB.insert(mock_db, title)
    db = DB.get_all_titles(mock_db)
    items = db.fetchall()
    assert len(items) == 1
    assert 'Alien' in str(items)

def test_update(monkeypatch, mock_db):
    alien = movies.Movie(Title='Alien', Awards='Won 1 Oscar. Another 16 wins & 19 nominations.')
    DB.insert(mock_db, alien)
    DB.update(mock_db, alien)
    db = DB.get_by_title(mock_db, alien)
    item = db.fetchone()
    assert 'Alien' in str(item)
    assert 'Won 1 Oscar. Another 16 wins & 19 nominations.' in str(item)


def test_sort_by(monkeypatch, mock_db_populated):
    db = DB.get_sorted_by(mock_db_populated, 'year')
    items = db.fetchall()
    assert len(items) == 5
    assert '2014' in str(items[0])
    assert '2000' in str(items[1])
    assert '1994' in str(items[2])
    assert '1994' in str(items[3])
    assert '1979' in str(items[4])

def test_filter_by_director(monkeypatch, mock_db_populated):
    db = DB.get_filtered_by_director(mock_db_populated, 'Ridley Scott')
    items = db.fetchall()
    assert len(items) == 1
    assert 'Alien' in str(items)

def test_filter_by_actor(monkeypatch, mock_db_populated):
    db = DB.get_filtered_by_actor(mock_db_populated, 'Sigourney Weaver')
    items = db.fetchall()
    assert len(items) == 1
    assert 'Alien' in str(items)

def test_filter_oscar_nominated(monkeypatch, mock_db_populated):    
    db = DB.get_oscar_nominated(mock_db_populated)
    items = db.fetchall()
    assert len(items) == 2
    assert 'Alien' not in str(items)
    assert 'Memento' in str(items)
    assert 'The Shawshank Redemption' in str(items)

def test_filter_won_more_than_80_percent(monkeypatch, mock_db_populated):    
    db = DB.get_all_titles(mock_db_populated)
    all_movies = db.fetchall()
    db = DB.get_won_more_than_80_percent(mock_db_populated)
    filtered = db.fetchall()
    assert len(all_movies) == 5
    assert len(filtered) == 3
    assert 'Alien' in str(all_movies)
    assert 'Alien' in str(filtered)
    assert 'Forrest Gump' in str(all_movies)
    assert 'Forrest Gump' not in str(filtered)
    assert 'The Shawshank Redemption' in str(all_movies)
    assert 'The Shawshank Redemption' not in str(filtered)
    
def test_filter_boxoffice_over_hundred_million(monkeypatch, mock_db_populated):
    db = DB.get_boxoffice_over_hundred_million(mock_db_populated)
    filtered = db.fetchall()
    assert len(filtered) == 1
    assert 'Alien' not in str(filtered)
    assert 'Forrest Gump' in str(filtered)

def test_filter_by_language(monkeypatch, mock_db_populated):
    db = DB.get_by_language(mock_db_populated, 'Spanish')
    filtered = db.fetchall()
    assert len(filtered) == 1
    assert 'Alien' not in str(filtered)
    assert 'Boyhood' in str(filtered)
