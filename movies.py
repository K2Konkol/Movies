import requests
import json
import re
import sqlite3 as db

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
        genre=data['Genre'],
        director=data['Director'],
        cast=data['Actors'],
        writer=data['Writer'],
        language=data['Language'],
        country=data['Country'],
        awards=data['Awards'],
        imdb_rating=data['imdbRating'],
        imdb_votes=data['imdbVotes'],
        box_office=data['BoxOffice']
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

    def __init__(self, title, year='N/A', runtime='N/A', genre = 'N/A', director='N/A', cast='N/A', writer='N/A', 
    language='N/A', country='N/A', awards='N/A', imdb_rating='N/A', imdb_votes='N/A', box_office='N/A'):
        self.title = title
        self.year = year
        self.runtime = runtime
        self.genre = genre
        self.director = director
        self.cast = cast
        self.writer = writer
        self.language = language
        self.country = country
        self.awards = awards
        self.IMDb_Rating = imdb_rating
        self.IMDb_votes = imdb_votes
        self.box_office = box_office

    def __str__(self):
        return self.title

class DB:
    """ Database class """  
    def __init__(self):
        self.conn = db.connect('movies.sqlite')
        self.cursor = self.conn.cursor()

    def insert(self, movie):
        return self.cursor.execute("insert into movies ('title') select :Title where not exists (select 1 from movies where title=:Title)",  movie)

    def update(self, movie):
        return self.cursor.execute("""update movies set year=:Year, runtime=:Runtime, genre=:Genre, director=:Director, cast=:Actors, writer=:Writer, language=:Language, country=:Country, awards=:Awards, imdb_rating=:imdbRating, imdb_votes=:imdbVotes, box_office=:BoxOffice where title=:Title""", movie)

    def get_all_titles(self):
        return self.cursor.execute("select title from movies")

    def get_by_title(self, movie):
        return self.cursor.execute("select * from movies where title=:Title", movie)


# ee = DB()
# ee.insert()
# ee.update()
# heh = ee.get_all_titles()
# print(heh.fetchall())