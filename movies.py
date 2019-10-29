import requests


def get_movie(url):
    res = requests.get(url)
    return res.json()
