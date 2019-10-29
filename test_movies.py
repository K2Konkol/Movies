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
    assert 'Actors' in result

