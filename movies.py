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
        d = ''
        box_office = (d.join(filter(lambda x : x.isdigit(), data['BoxOffice'])))
        box_office = int(box_office) if len(box_office) > 1 else 0
        
        return Movie(
        Title=data['Title'], 
        Year=data['Year'],
        Runtime=data['Runtime'],
        Genre=data['Genre'],
        Director=data['Director'],
        Cast=data['Actors'],
        Writer=data['Writer'],
        Language=data['Language'],
        Country=data['Country'],
        Awards=data['Awards'],
        imdb_Rating=data['imdbRating'],
        imdb_Votes=data['imdbVotes'],
        Box_Office=box_office
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

def dict_from_class(cls):
    return dict((key, value) for (key, value) in cls.__dict__.items())

class Movie:
    """ Movie custom class """

    def __init__(self, Title, Year='N/A', Runtime='N/A', Genre = 'N/A', Director='N/A', Cast='N/A', Writer='N/A', 
    Language='N/A', Country='N/A', Awards='N/A', imdb_Rating='N/A', imdb_Votes='N/A', Box_Office='N/A'):
        self.Title = Title
        self.Year = Year
        self.Runtime = Runtime
        self.Genre = Genre
        self.Director = Director
        self.Cast = Cast
        self.Writer = Writer
        self.Language = Language
        self.Country = Country
        self.Awards = Awards
        self.imdb_Rating = imdb_Rating
        self.imdb_Votes = imdb_Votes
        self.Box_Office = Box_Office

    def __str__(self):
        return self.title


class DB:
    """ Database class """  
    def __init__(self):
        self.conn = db.connect('movies.sqlite')
        self.cursor = self.conn.cursor(prepared=True)

    def insert(self, movie):
        params = dict_from_class(movie)
        return self.cursor.execute("insert into movies ('title') select :Title where not exists (select 1 from movies where title=:Title)",  params)

    def update(self, movie):
        params = dict_from_class(movie)
        return self.cursor.execute("update movies set Year=:Year, Runtime=:Runtime, Genre=:Genre, Director=:Director, Cast=:Cast, Writer=:Writer, Language=:Language, Country=:Country, Awards=:Awards, imdb_Rating=:imdb_Rating, imdb_Votes=:imdb_Votes, Box_Office=:Box_Office where title=:Title", params)

    def get_all_titles(self):
        return self.cursor.execute("select title from movies")

    def get_by_title(self, movie):
        params = dict_from_class(movie)
        return self.cursor.execute("select * from movies where title=:Title", params)

    def get_sorted_by(self, *args):
        column = ""
        for arg in args:
            column = arg+", " + column
        query = ""f"select title, {column[:-2]} from movies order by {column[:-2]} desc"""
        return self.cursor.execute(query)

    def get_filtered_by_director(self, director):
        param = ('%'+director+'%',)
        return self.cursor.execute("select title from movies where director like ?", param)

    def get_filtered_by_actor(self, actor):
        param = ('%'+actor+'%',)
        return self.cursor.execute("select title from movies where movies.cast like ?", param)

    def get_oscar_nominated(self):
        return self.cursor.execute("select title from movies where awards like 'Nominated%'")

    def get_won_more_than_80_percent(self):
        def regexp(expr, item):
            m = re.search(expr, item)
            wins = float(m.group(1))
            nominations = float(m.group(3))        
            return wins/nominations > 0.8
        
        self.conn.create_function("REGEXP", 2, regexp)
        expr = (r'(\d*)\s\b(\w*wins\w*)\b\s.\s(\d*)\s\b(\w*nomination*\w*)\b.*$',)
        return self.cursor.execute("""select * from movies where awards regexp ?""", expr)

    def get_boxoffice_over_hundred_million(self):
        return self.cursor.execute("select title, box_office from movies where box_office > '100000000'")

    def get_by_language(self, language):
        param = ('%'+language+'%',)
        return self.cursor.execute("select title, language from movies where language like ?", param)