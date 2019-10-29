import requests


def get_movie(url, params):
    res = requests.get(url, params)
    return res.json()
