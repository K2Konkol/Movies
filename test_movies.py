import pytest
import requests
import movies

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
    assert alien.actors == 'Tom Skerritt, Sigourney Weaver, Veronica Cartwright, Harry Dean Stanton'
    assert alien.oscars_won == '1'
    assert alien.oscar_nominations == 'N/A'
    assert alien.another_wins == '16'
    assert alien.another_nominations == '19'
