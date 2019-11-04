""" CLI application fetching data from OMDb API and storing in local sqlite database """
import json
import re
import sqlite3 as db
import argparse
from sqlite3 import OperationalError as oe
import requests

URL = 'http://omdbapi.com/'
    
def populate_db(database):
    """ Populates database with data from API"""
    print("Downloading data from OMDb...")
    c = database.get_all_titles()
    movie_list = c.fetchall()
    key = get_apikey()['apikey']
    for (title, ) in movie_list: 
        params = dict(apikey=key, t=title, type='movie')
        response = get_movie(URL, params=params)
        movie = json_to_movie(response)
        database.update(movie)
        print(f"Succesfully retrieved data from OMDb for {title}\n")

def get_apikey():
    """ Gets API key from JSON"""
    with open('apikey.json', 'r') as f:
        apikey = json.load(f)
    return apikey

def get_movie(url, params):
    """ Gets movie data from API"""
    res = requests.get(url, params)
    return res.json()

def str_to_int(string):
    """ Parse string to int """
    s = ''    
    try:
        i = (s.join(filter(lambda x: x.isdigit(), string)))
    except TypeError:
        i = 0 
    return int(i) if i else 0

def json_to_movie(data):    
    """ Parse JSON data to Movie object """
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

def get_oscars(data):
    """ Gets oscars """
    p = r'\b(\w*Won\w*)\b\s(\d*)\s\b(\w*Oscar*\w*)\b'
    m = re.search(p, data)
    oscars = int(m.group(2)) if m is not None else 0
    return oscars

def get_awards(data):
    """ Gets awards """
    p = r'(\d*)\s\b(\w*wins\w*)\b\s.\s(\d*)\s\b(\w*nomination*\w*)\b'
    m = re.search(p, data)
    awards = int(m.group(1)) if m is not None else 0
    return awards

def get_nominations(data):
    """ Gets nominations """
    p = r'(\d*)\s\b(\w*wins\w*)\b\s.\s(\d*)\s\b(\w*nomination*\w*)\b'
    m = re.search(p, data)
    nominations = int(m.group(3)) if m is not None else 0
    return nominations

def dict_from_class(cls):
    """ Returns dictionary from Movie class"""
    return dict((key, value) for (key, value) in cls.__dict__.items())

class Movie:
    """ Movie class """

    def __init__(self, title='N/A', year=0, runtime='N/A', genre='N/A', director='N/A', cast='N/A', writer='N/A', 
    language='N/A', country='N/A', awards='N/A', imdb_rating=0.0, imdb_votes=0, box_office=0):
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
        self.imdb_rating = imdb_rating
        self.imdb_votes = imdb_votes
        self.box_office = box_office

    def __str__(self):
        return self.title


class DB:
    """ Database class """  
    
    def __init__(self): 
        self.conn = db.connect('movies.sqlite')
        self.cursor = self.conn.cursor()

    def insert(self, movie):
        """ Inserts movie title to database"""
        params = (movie, )
        return self.cursor.execute("insert into movies ('title') select :title where not exists (select 1 from movies where title=:title)", params)

    def update(self, movie):
        """ Updates movie data in database"""
        params = dict_from_class(movie)
        return self.cursor.execute("update movies set year=:year, runtime=:runtime, genre=:genre, director=:director, cast=:cast, writer=:writer, language=:language, country=:country, awards=:awards, imdb_rating=:imdb_rating, imdb_votes=:imdb_votes, box_office=:box_office where title=:title", params)

    def get_all_titles(self):
        """ Gets all movie titles from database """
        return self.cursor.execute("select title from movies")

    def get_all(self):
        """ Gets all records from database """
        return self.cursor.execute("select * from movies")

    def get_by_title(self, movie):
        """ Gets movie by title """
        params = dict_from_class(movie)
        return self.cursor.execute("select * from movies where title=:title", params)

    def get_sorted_by(self, column):
        """ Gets movies sorted by given column """
        query = ""f"select title, {column} from movies order by {column} desc"""
        return self.cursor.execute(query)

    def get_sorted_by_runtime(self):
        """ Gets movies sorted by given column """
        def str_to_int(item):
            """ Regex helper function"""
            s = ''
            try:
                i = (s.join(filter(lambda x: x.isdigit(), item)))
            except TypeError:
                i = 0 
            return int(i) if i else 0
        self.conn.create_function("STR_TO_INT", 1, str_to_int)  
        return self.cursor.execute("select title, runtime from movies order by cast(str_to_int(runtime) as int) desc")

    def get_filtered_by_director(self, director):
        """ Gets movies filtered by director """
        param = ('%'+director+'%',)
        return self.cursor.execute("select title, director from movies where director like ?", param)

    def get_filtered_by_actor(self, actor):
        """ Gets movies filtered by actor """
        param = ('%'+actor+'%',)
        return self.cursor.execute("select title, movies.cast from movies where movies.cast like ?", param)

    def get_oscar_nominated(self):
        """ Gets movies nominated to Oscar """
        return self.cursor.execute("select title, awards from movies where awards like 'nominated%'")

    def get_awards_column(self):
        """ Gets movies titles with awards """
        return self.cursor.execute("select title, awards from movies")

    def get_boxoffice_over_hundred_million(self):
        """ Gets movies with income over $100 mln """
        def str_to_int(item):
            """ Regex helper function"""
            s = ''
            try:
                i = (s.join(filter(lambda x: x.isdigit(), item)))
            except TypeError:
                i = 0 
            return int(i) if i else 0
        self.conn.create_function("STR_TO_INT", 1, str_to_int)  
        return self.cursor.execute("select title, box_office from movies where cast(str_to_int(box_office) as int) > '100000000'")

    def get_by_language(self, language):
        """ Gets movies filtered by language """
        param = ('%'+language+'%', )
        return self.cursor.execute("select title, language from movies where language like ?", param)

    def compare_imdb_rating(self, movie1, movie2):
        """ Compares two given movies by rating """
        params = (movie1, movie2, )
        return self.cursor.execute("select title from (select title, max(imdb_rating) from (select title, imdb_rating from movies where title=? union select title, imdb_rating from movies where title=?))", params)

    def get_box_office(self, movie1, movie2):
        """ Gets two given movies by box office """
        params = (movie1, movie2, )
        return self.cursor.execute("select title, box_office from (select title, box_office from movies where title=? union select title, box_office from movies where title=?)", params)

    def get_awards(self, movie1, movie2):
        """ Helper function to compare awards """
        params = (movie1, movie2, )
        return self.cursor.execute("select title, awards from movies where title=? union select title, awards from movies where title=?", params)

    def get_runtime(self, movie1, movie2):
        """ Helper funtion to compare runtime """
        params = (movie1, movie2, )
        return self.cursor.execute("select title, runtime from movies where title=? union select title, runtime from movies where title=?", params)

    def get_for_highscores(self):
        """ Helper funtion to compare highscores """
        return self.cursor.execute("select title, runtime, box_office, awards, imdb_rating from movies")

def compare_awards(movies):
    """ Compares given awards """
    movie1 = movies[0]
    movie2 = movies[1]
    return movie1[0] if get_awards(movie1[1]) > get_awards(movie2[1]) else movie2[0]

def compare_box_office(movies):
    """ Compares given box offices """
    movie1 = movies[0]
    movie2 = movies[1]
    return movie1[0] if str_to_int(movie1[1]) > str_to_int(movie2[1]) else movie2[0]
def compare_runtime(movies):      
    """ Compares given runtime """
    movie1 = movies[0]
    movie2 = movies[1]
    return movie1[0] if str_to_int(movie1[1]) > str_to_int(movie2[1]) else movie2[0]

def get_highest_runtime(movies):
    """ Helper function getting highest runtime """
    highest_runtime = ('', '')
    for movie in movies:
        if movie[1] is not None and int(str_to_int(movie[1])) > int(str_to_int(highest_runtime[1])):
            highest_runtime = (movie[0], movie[1])
    return highest_runtime

def get_highest_box_office(movies):
    """ Helper function getting highest box office """
    highest_box_office = ('', '')
    for movie in movies:
        if movie[2] is not None and int(str_to_int(movie[2])) > int(str_to_int(highest_box_office[1])):
            highest_box_office = (movie[0], movie[2])
    return highest_box_office

def get_oscars_highscore(movies):
    """ Helper function getting highest oscar wins """
    oscar_highscore = ('', 0)
    for movie in movies:
        oscars = get_oscars(movie[3]) if movie[3] is not None else 0
        if oscars > int(oscar_highscore[1]):
            oscar_highscore = (movie[0], oscars)
    return oscar_highscore

def get_nominations_highscore(movies):
    """ Helper function getting nominations highscore """
    nominations_highscore = ('', 0)
    for movie in movies:
        nominations = get_nominations(movie[3]) if movie[3] is not None else 0
        if nominations > int(nominations_highscore[1]):
            nominations_highscore = (movie[0], nominations)
    return nominations_highscore

def get_awards_highscore(movies):
    """ Helper function getting awards highscore """
    awards_highscore = ('', 0)
    for movie in movies:
        awards = get_awards(movie[3]) if movie[3] is not None else 0
        if awards > int(awards_highscore[1]):
            awards_highscore = (movie[0], awards)
    return awards_highscore

def get_highest_imdb_rating(movies):
    """ Helper function getting highest rating """
    highest_rating = ('', 0.0)
    for movie in movies:
        rating = movie[4] if movie[4] is not None else 0
        if rating > int(highest_rating[1]):
            highest_rating = (movie[0], rating)
    return highest_rating

def get_width(data):
    """ Helper function getting table width """
    width = 2
    max_length = 5
    for item in data:
        if len(str((item[0]))) > max_length:
            max_length = len(item[0])
    return width+max_length 

def main():
    """ Main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--populate", help="Use this option to download data from OMDb and populate your database", action="store_true")
    parser.add_argument("-f", "--filter_by", help="Filtering by column", action='store', nargs='*', type=str)
    parser.add_argument("--highscores", help="Show Highscores", action='store_true')
    parser.add_argument("-c", "--compare", help="Compare two movie titles by given column", action='store', nargs='*', type=str)
    parser.add_argument("-a", "--add", help="Add movie to database", action='store', nargs='*', type=str)
    parser.add_argument("-s", "--sort_by", help="Sort output data by one or multiple columns", action='store', nargs='+', choices=['title', 'year', 'runtime', 'genre', 'director', 'cast', 'writer', 'language', 'country', 'awards', 'imdb_rating', 'imdb_votes', 'box_office'])

    args = parser.parse_args()  

    moviedb = DB()

    if args.populate:
        populate_db(moviedb)
        moviedb.conn.commit()
        print("Succesfully populated database")

    if args.highscores:
        c = moviedb.get_for_highscores()
        res = c.fetchall()
        rtm = get_highest_runtime(res)
        bo = get_highest_box_office(res)
        awrds = get_awards_highscore(res)
        ntns = get_nominations_highscore(res)
        oscr = get_oscars_highscore(res)
        rtng = get_highest_imdb_rating(res)
        rows = ['Runtime', 'Box Office', 'Awards', 'Nominations', 'Oscars', 'IMDb Rating']
        result = [rtm, bo, awrds, ntns, oscr, rtng]
        highscores = zip(rows, result)
        width = get_width(result)
        for column, (title, value) in highscores:
            print(str(column).ljust(13), str(title).ljust(width), value)

    if args.sort_by:
        if args.sort_by[0] == 'cast':
            args.sort_by[0] = 'movies.cast'
        
        if args.sort_by[0] == 'runtime':
            c = moviedb.get_sorted_by_runtime()
        else:    
            c = moviedb.get_sorted_by(args.sort_by[0])
        try:
            result = c.fetchall()    
        except TypeError:
            pass
        width = get_width(result)      
        print('Title'.ljust(width), args.sort_by[0].ljust(width).title())
        for title, value in result:
            print(str(title).ljust(width), str(value).ljust(width))

    if args.filter_by:
        if args.filter_by[0] == 'director':
            c = moviedb.get_filtered_by_director(args.filter_by[1])
            result = c.fetchall()
            width = get_width(result)      
            print('Title'.ljust(width), 'Director'.ljust(width))
            for title, value in result:
                print(str(title).ljust(width), value.ljust(width))

        elif args.filter_by[0] == 'actor':
            c = moviedb.get_filtered_by_actor(args.filter_by[1])
            result = c.fetchall()
            width = get_width(result)      
            print('Title'.ljust(width), 'Cast'.ljust(width))
            for title, value in result:
                print(str(title).ljust(width), value.ljust(width))

        elif args.filter_by[0] == 'nominated':
            c = moviedb.get_oscar_nominated()
            result = c.fetchall()
            width = get_width(result)      
            print('Title'.ljust(width), 'Awards'.ljust(width))
            for title, value in result:
                print(str(title).ljust(width), value.ljust(width))

        elif args.filter_by[0] == 'awarded':
            db.enable_callback_tracebacks(True)
            c = moviedb.get_awards_column()
            result = c.fetchall()
            awarded = []
            for movie in result:
                wins = get_awards(str(movie))
                nominations = get_nominations(str(movie))
                if nominations is not 0 and wins/nominations > 0.8:
                    awarded.append(movie) 
            width = get_width(awarded)      
            print('Title'.ljust(width), 'Awards'.ljust(width))
            for title, value in awarded:
                print(str(title).ljust(width), value)
                
        elif args.filter_by[0] == 'earned':
            db.enable_callback_tracebacks(True)
            c = moviedb.get_boxoffice_over_hundred_million()
            result = c.fetchall()
            width = get_width(result)      
            print('Title'.ljust(width), 'Box Office'.ljust(width))
            for title, value in result:
                print(str(title).ljust(width), value.ljust(width))   

        elif args.filter_by[0] == 'language':
            db.enable_callback_tracebacks(True)
            c = moviedb.get_by_language(args.filter_by[1])
            result = c.fetchall()
            width = get_width(result)      
            print('Title'.ljust(width), 'Language'.ljust(width))
            for title, value in result:
                print(str(title).ljust(width), value.ljust(width))
        if list(args.filter_by) == [] or args.filter_by[0] not in ['director', 'actor', 'language', 'awarded', 'nominated', 'earned']:
            print("usage: movies.py [-f] filter - choose from: ['director', 'actor', 'language', 'awarded', 'nominated', 'earned']")

    if args.add:
        title = args.add[0]
        c = moviedb.insert(title)
        print(f'Succesfully added {title} to database')
        key = get_apikey()['apikey']
        params = dict(apikey=key, t=title, type='movie')
        
        try:
            response = get_movie(URL, params=params)
            movie = json_to_movie(response)
            moviedb.update(movie)
            print(f"Succesfully retrieved data from OMDb for {title}\n")            
            moviedb.conn.commit()
        except:
            print(f"Couldn't find data in OMDb - rolling back {title}\n")
            moviedb.conn.rollback()
        
    if args.compare:
        if args.compare[0] == 'imdb_rating':
            c = moviedb.compare_imdb_rating(args.compare[1], args.compare[2])
            result = c.fetchone()
            print(result[0])

        if args.compare[0] == 'runtime':
            c = moviedb.get_runtime(args.compare[1], args.compare[2])
            result = c.fetchall()
            winner = compare_runtime(result)
            print(winner)

        if args.compare[0] == 'box_office':
            c = moviedb.get_box_office(args.compare[1], args.compare[2])
            result = c.fetchall()
            winner = compare_box_office(result)
            print(winner)
        
        if args.compare[0] == 'awards':
            c = moviedb.get_awards(args.compare[1], args.compare[2])
            result = c.fetchall()
            winner = compare_awards(result)
            print(winner)

if __name__ == '__main__':
    main()
