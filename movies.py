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

def str_to_int(string):
    s = ''
    i = (s.join(filter(lambda x : x.isdigit(), string)))
    return int(i) if len(i) > 0 else 0

def json_to_movie(data):    
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
        Box_Office=data['BoxOffice']
        )

def get_oscars(data):
    m = re.search(r'\b(\w*Won\w*)\b\s(\d*)\s\b(\w*Oscar*\w*)\b', data)
    oscars = int(m.group(2)) if m else 0
    return oscars

def get_awards(data):
    m = re.search(r'(\d*)\s\b(\w*wins\w*)\b\s.\s(\d*)\s\b(\w*nomination*\w*)\b', data)
    awards = int(m.group(1)) if m else 0
    return awards

def get_nominations(data):
    m = re.search(r'(\d*)\s\b(\w*wins\w*)\b\s.\s(\d*)\s\b(\w*nomination*\w*)\b', data)
    nominations = int(m.group(3)) if m else 0
    return nominations

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
        def str_to_int(item):
            s = ''
            i = (s.join(filter(lambda x : x.isdigit(), item)))
            return int(i) if len(i) > 0 else 0
            
        self.conn.create_function("STR_TO_INT", 1, str_to_int)  
        return self.cursor.execute("select title, box_office from movies where cast(str_to_int(box_office) as int) > '100000000'")

    def get_by_language(self, language):
        param = ('%'+language+'%',)
        return self.cursor.execute("select title, language from movies where language like ?", param)

    def compare_imdb_rating(self, movie1, movie2):
        params = (movie1, movie2,)
        return self.cursor.execute("select title from (select title, max(imdb_rating) from (select title, imdb_rating from movies where title=? union select title, imdb_rating from movies where title=?))", params)

    def compare_box_office(self, movie1, movie2):
        params = (movie1, movie2,)
        return self.cursor.execute("select title from (select title, max(box_office) from (select title, box_office from movies where title=? union select title, box_office from movies where title=?))", params)

    def get_awards(self, movie1, movie2):
        params = (movie1, movie2,)
        return self.cursor.execute("select title, awards from movies where title=? union select title, awards from movies where title=?", params)

    def get_runtime(self, movie1, movie2):
        params = (movie1, movie2,)
        return self.cursor.execute("select title, runtime from movies where title=? union select title, runtime from movies where title=?", params)

    def get_for_highscores(self):
        return self.cursor.execute("select title, runtime, box_office, awards, imdb_rating from movies")

def compare_awards(movies):      
    movie1 = movies[0]
    movie2 = movies[1]
    return movie1[0] if get_awards(movie1[1]) > get_awards(movie2[1]) else movie2[0]

def compare_runtime(movies):      
    movie1 = movies[0]
    movie2 = movies[1]
    return movie1[0] if str_to_int(movie1[1]) > str_to_int(movie2[1]) else movie2[0]

def get_highest_runtime(movies):
    highest_runtime = ('','')
    for movie in movies:
        if int(str_to_int(movie[1])) > int(str_to_int(highest_runtime[1])):
            highest_runtime = (movie[0],movie[1])
    return highest_runtime

def get_highest_box_office(movies):
    highest_box_office = ('','')
    for movie in movies:
        if int(str_to_int(movie[2])) > int(str_to_int(highest_box_office[1])):
            highest_box_office = (movie[0],movie[2])
    return highest_box_office

def get_oscars_highscore(movies):
    oscar_highscore = ('',0)
    for movie in movies:
        oscars = get_oscars(movie[3])
        if oscars > int(oscar_highscore[1]):
            oscar_highscore = (movie[0],oscars)
    return oscar_highscore

def get_nominations_highscore(movies):
    nominations_highscore = ('',0)
    for movie in movies:
        nominations = get_nominations(movie[3])
        if nominations > int(nominations_highscore[1]):
            nominations_highscore = (movie[0],nominations)
    return nominations_highscore

def get_awards_highscore(movies):
    awards_highscore = ('',0)
    for movie in movies:
        awards = get_awards(movie[3])
        if awards > int(awards_highscore[1]):
            awards_highscore = (movie[0],awards)
    return awards_highscore

def get_highest_imdb_rating(movies):
    highest_rating = ('',0.0)
    for movie in movies:
        rating = movie[4]
        if rating > int(highest_rating[1]):
            highest_rating = (movie[0],rating)
    return highest_rating