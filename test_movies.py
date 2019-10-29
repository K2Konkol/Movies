import pytest
import requests
import movies

FAKE_URL = 'http://fake_url'


class MockResponse:
    @staticmethod
    def json():
        import json
        with open('alien.json', 'r') as read_file:
            data = json.load(read_file)
        return data


@pytest.fixture
def mock_response(monkeypatch):

    def mock_get(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(requests, 'get', mock_get)


def test_get_movie(mock_response):
    result = movies.get_movie(FAKE_URL)
    assert 'Actors' in result

