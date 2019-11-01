import requests
import json
import re


def get_apikey():
    with open('apikey.json', 'r') as f:
        apikey = json.load(f)
    return apikey

def get_movie(url, params):
    res = requests.get(url, params)
    return res.json()

def json_to_movie(data):
    awards = parse_awards(data['Awards'])
    return Movie(
        title=data['Title'], 
        year=data['Year'],
        runtime=data['Runtime'],
        director=data['Director'],
        language=data['Language'],
        actors=data['Actors'],
        oscars_won=awards['oscars_won'],
        oscar_nominations=awards['oscar_nominations'],
        another_wins=awards['another_wins'],
        another_nominations=awards['another_nominations'],
        boxoffice=data['BoxOffice'],
        imdbRating=data['imdbRating'],
        imdbID=data['imdbID']
        )

def parse_awards(data):
    m1 = re.search(r'\b(\w*Won\w*)\b\s(\d*)\s\b(\w*Oscar*\w*)\b', data)
    m2 = re.search(r'\b(\w*Nominated for\w*)\b\s(\d*)\s\b(\w*Oscar*\w*)\b', data)
    m3 = re.search(r'(\d*)\s\b(\w*wins\w*)\b\s.\s(\d*)\s\b(\w*nomination*\w*)\b', data)
    oscars_won = m1.group(2) if m1 else 'N/A'
    oscar_nominations = m2.group(2) if m2 else 'N/A'
    another_wins = m3.group(1) if m3 else 'N/A'
    another_nominations = m3.group(3) if m3 else 'N/A'
    awards = {
        "oscars_won":oscars_won,
        "oscar_nominations":oscar_nominations,
        "another_wins":another_wins,
        "another_nominations":another_nominations
    }
    return awards


class Movie:
    """ Movie custom class """

    def __init__(self, title, year='N/A', runtime='N/A', director='N/A', language='N/A', actors='N/A', oscar_nominations='N/A', oscars_won='N/A',
    another_wins='N/A', another_nominations='N/A', boxoffice='N/A', imdbRating='N/A', imdbID='N/A'):
        self.title = title
        self.year = year
        self.runtime = runtime
        self.director = director
        self.language = language
        self.actors = actors
        self.oscars_won = oscars_won
        self.oscar_nominations = oscar_nominations
        self.another_wins = another_wins
        self.another_nominations = another_nominations
        self.boxoffice = boxoffice
        self.imdbRating = imdbRating
        self.imdbID = imdbID

    def __str__(self):
        return self.title

