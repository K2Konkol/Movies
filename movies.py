""" CLI application fetching data from OMDb API and storing in local sqlite database """
import json
import re
import sqlite3 as sql
import argparse
from sqlite3 import OperationalError as oe
import requests

URL = 'http://omdbapi.com/'

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

class Highscore():
    def __init__(self):
        self.highest_runtime = ('', '')
        self.highest_box_office = ('', '')
        self.oscar_highscore = ('', 0)
        self.nominations_highscore = ('', 0)
        self.awards_highscore = ('', 0)
        self.highest_rating = ('', 0.0)

    def get_highest_runtime(self, movies):
        highest_runtime = self.highest_runtime
        for movie in movies:
            if movie[1] is not None and int(str_to_int(movie[1])) > int(str_to_int(highest_runtime[1])):
                highest_runtime = (movie[0], movie[1])
        return highest_runtime

    def get_highest_box_office(self, movies):
        highest_box_office = self.highest_box_office
        for movie in movies:
            if movie[2] is not None and int(str_to_int(movie[2])) > int(str_to_int(highest_box_office[1])):
                highest_box_office = (movie[0], movie[2])
        return highest_box_office

    def get_highest_imdb_rating(self, movies):
        highest_rating = self.highest_rating
        for movie in movies:
            rating = movie[4] if movie[4] is not None else 0
            if rating > int(highest_rating[1]):
                highest_rating = (movie[0], rating)
        return highest_rating

    def get_oscars_highscore(self, movies):
        """ Helper function getting highest oscar wins """
        oscar_highscore = self.oscar_highscore
        for movie in movies:
            oscars = get_oscars(movie[3]) if movie[3] is not None else 0
            if oscars > int(oscar_highscore[1]):
                oscar_highscore = (movie[0], oscars)
        return oscar_highscore

    def get_nominations_highscore(self, movies):
        """ Helper function getting nominations highscore """
        nominations_highscore = self.nominations_highscore
        for movie in movies:
            nominations = get_nominations(movie[3]) if movie[3] is not None else 0
            if nominations > int(nominations_highscore[1]):
                nominations_highscore = (movie[0], nominations)
        return nominations_highscore

    def get_awards_highscore(self, movies):
        """ Helper function getting awards highscore """
        awards_highscore = self.awards_highscore
        for movie in movies:
            awards = get_awards(movie[3]) if movie[3] is not None else 0
            if awards > int(awards_highscore[1]):
                awards_highscore = (movie[0], awards)
        return awards_highscore

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
        self.conn = sql.connect('movies.sqlite')
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
        param = ('%'+actor+'%', )
        return self.cursor.execute("select title, movies.cast from movies where movies.cast like ?", param)

    def get_filtered_by(self, filter, value):
        """ Gets movies filtered by given value """
        params = ('%'+value+'%', )
        return self.cursor.execute(f"select title, {filter} from movies where {filter} like ?", params)

    def get_oscar_nominated(self):
        """ Gets movies nominated to Oscar """
        return self.cursor.execute("select title, awards from movies where awards like 'nominated%'")

    def get_awarded(self):
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

    def get_imdb_rating(self, movie1, movie2):
        """ Gets two given movies with rating """
        params = (movie1, movie2, )
        return self.cursor.execute("select title, imdb_rating from (select title, imdb_rating from movies where title like ? union select title, imdb_rating from movies where title like ?)", params)

    def get_box_office(self, movie1, movie2):
        """ Gets two given movies with box office """
        params = (movie1, movie2, )
        return self.cursor.execute("select title, box_office from (select title, box_office from movies where title like ? union select title, box_office from movies where title like ?)", params)

    def get_awards(self, movie1, movie2):
        """ Gets two given movies with awards """
        params = (movie1, movie2, )
        return self.cursor.execute("select title, awards from movies where title like ? union select title, awards from movies where title like ?", params)

    def get_runtime(self, movie1, movie2):
        """ Gets two given movies with box runtime """
        params = (movie1, movie2, )
        return self.cursor.execute("select title, runtime from movies where title like ? union select title, runtime from movies where title like ?", params)

    def get_for_highscores(self):
        """ Gets movies with columns for highscores """
        return self.cursor.execute("select title, runtime, box_office, awards, imdb_rating from movies")

class Compare():
    def __init__(self, movies):
        self.movie1 = movies[0]
        self.movie2 = movies[1]
        
    def compare(self):
        pass

class CompareNumeric(Compare):
    def compare(self):
        return self.movie1[0] if str_to_int(self.movie1[1]) > str_to_int(self.movie2[1]) else self.movie2[0]

class CompareAwards(Compare):
    def compare(self):
        return self.movie1[0] if get_awards(self.movie1[1]) > get_awards(self.movie2[1]) else self.movie2[0]

class Repository():
    def __init__(self):
        self.db = DB()

    def populate(self):
        """ Populates database with data from API"""
        print("Downloading data from OMDb...")
        cursor = self.db.get_all_titles()
        movie_list = cursor.fetchall()
        key = get_apikey()['apikey']
        for (title, ) in movie_list: 
            params = dict(apikey=key, t=title, type='movie')
            response = get_movie(URL, params=params)
            movie = json_to_movie(response)
            self.db.update(movie)
            print(f"Succesfully retrieved data from OMDb for {title}\n")
        self.db.conn.commit()

    def add(self, title):
        cursor = self.db.insert(title)
        print(f'Succesfully added {title} to database')
        key = get_apikey()['apikey']
        params = dict(apikey=key, t=title, type='movie')    
        try:
            response = get_movie(URL, params=params)
            movie = json_to_movie(response)
            self.db.update(movie)
            self.db.conn.commit()
            print(f"Succesfully retrieved data from OMDb for {title}\n") 
        except:
            self.db.conn.rollback()
            print(f"Couldn't find data in OMDb - rolling back {title}\n")

    def get_awards(self, movies):
        cursor = self.db.get_awards(movies[0],movies[1])
        return cursor.fetchall()

    def get_box_office(self, movies):
        cursor = self.db.get_box_office(movies[0],movies[1])
        return cursor.fetchall()
    
    def get_runtime(self, movies):
        cursor = self.db.get_runtime(movies[0],movies[1])
        return cursor.fetchall()

    def get_imdb_rating(self, movies):
        cursor = self.db.get_imdb_rating(movies[0],movies[1])
        return cursor.fetchall()

    def get_filtered_by(self, filter, value):
        cursor = self.db.get_filtered_by(filter, value)
        return cursor.fetchall()

    def get_awarded(self):
        cursor = self.db.get_awarded()
        return cursor.fetchall()

    def get_earned(self):
        cursor = self.db.get_boxoffice_over_hundred_million()
        return cursor.fetchall()

    def get_nominated(self):
        cursor = self.db.get_oscar_nominated()
        return cursor.fetchall()

    def get_highscores(self):
        highscore = Highscore()
        cursor = self.db.get_for_highscores()
        data = cursor.fetchall()
        runtime = highscore.get_highest_runtime(data)
        box_office = highscore.get_highest_box_office(data)
        awards = highscore.get_awards_highscore(data)
        nominations = highscore.get_nominations_highscore(data)
        oscars = highscore.get_oscars_highscore(data)
        rating = highscore.get_highest_imdb_rating(data)
        return [runtime, box_office, awards, nominations, oscars, rating]

    def get_sorted_by_runtime(self):
        cursor = self.db.get_sorted_by_runtime()
        return cursor.fetchall()

    def get_sorted_by(self, sorter):
        cursor = self.db.get_sorted_by(sorter)
        try:
            data =  cursor.fetchall()
        except TypeError:
            pass
        return data

class PrettyPrinter():
    def __init__(self, data):
        def get_width(data):
            """ Helper function getting table width """
            width = 2
            max_length = 5
            for item in data:
                if len(str((item[0]))) > max_length:
                    max_length = len(item[0])
            return width+max_length 
            
        self.width = get_width(data)

    def print(self, columns, data):
        pass

class PrintFiltered(PrettyPrinter):
    def print(self, columns, data):
        col1 = columns[0].title()
        col2 = columns[1].title()
        print(col1.ljust(self.width), col2.ljust(self.width))
        for (title, value) in data:
            print(str(title).ljust(self.width), str(value))

class PrintHighscores(PrettyPrinter):
    def print(self, data):
        rows = ['Runtime', 'Box Office', 'Awards', 'Nominations', 'Oscars', 'IMDb Rating']
        rows_width = 13
        highscores = zip(rows, data)
        for column, (title, value) in highscores:
                print(str(column).ljust(rows_width), str(title).ljust(self.width), value)

class Main():
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-p", "--populate", help="Use this option to download data from OMDb and populate your database", action="store_true")
        self.parser.add_argument("-f", "--filter_by", help="Filtering by column", action='store', nargs='*', type=str)
        self.parser.add_argument("--highscores", help="Show Highscores", action='store_true')
        self.parser.add_argument("-c", "--compare", help="Compare two movie titles by given column", action='store', nargs='*', type=str)
        self.parser.add_argument("-a", "--add", help="Add movie to database", action='store', nargs='*', type=str)
        self.parser.add_argument("-s", "--sort_by", help="Sort output data by one or multiple columns", action='store', nargs='+', choices=['title', 'year', 'runtime', 'genre', 'director', 'cast', 'writer', 'language', 'country', 'awards', 'imdb_rating', 'imdb_votes', 'box_office'])
        
    def main(self):
        """ Main function"""
        args = self.parser.parse_args()
        repo = Repository()

        if args.populate:
            print(repo.populate())

        if args.highscores:
            data = repo.get_highscores()
            PrintHighscores(data).print(data)
            
        if args.sort_by:
            sorter = args.sort_by[0]
            columns = ('Title', sorter)
            if sorter == 'cast':
                sorter = 'movies.cast'
            if sorter == 'runtime':
                data = repo.get_sorted_by_runtime()
            else:    
                data = repo.get_sorted_by(sorter)
            PrintFiltered(data).print(columns, data)

        if args.filter_by:
            choices = ['director', 'actor', 'language', 'awarded', 'nominated', 'earned']
            if list(args.filter_by) == [] or args.filter_by[0] not in choices:
                print(f"usage: movies.py [-f] filter - choose from: {choices}")
                pass
            
            filter = args.filter_by[0]
            if args.filter_by[0] not in ['nominated', 'awarded', 'earned']:
                pass
            else:
                value = args.filter_by[1] 
            
            if filter == 'director':
                columns = ('Title', filter)
                data = repo.get_filtered_by(filter, value)
                PrintFiltered(data).print(columns, data)
                
            if filter == 'actor':
                columns = ('Title', filter)
                filter = 'movies.cast'
                data = repo.get_filtered_by(filter, value)
                PrintFiltered(data).print(columns, data)

            if filter == 'language':
                columns = ('Title', filter)
                data = repo.get_filtered_by(filter, value)
                PrintFiltered(data).print(columns, data)

            if filter == 'nominated':
                columns = ('Title', filter)
                data = repo.get_nominated()
                PrintFiltered(data).print(columns, data)

            if filter == 'awarded':
                columns = ('Title', filter)
                data = repo.get_awarded()
                awarded = []
                for movie in data:
                    wins = get_awards(str(movie))
                    nominations = get_nominations(str(movie))
                    if nominations is not 0 and wins/nominations > 0.8:
                        awarded.append(movie) 
                PrintFiltered(awarded).print(columns, awarded)
                    
            if filter == 'earned':
                columns = ('Title', filter)
                data = repo.get_earned()
                PrintFiltered(data).print(columns, data)

        if args.add:
            title = args.add[0]
            repo.add(title)
            
        if args.compare:
            comparator = args.compare[0]
            movies = (args.compare[1], args.compare[2])

            if comparator == 'imdb_rating':
                print(CompareNumeric(repo.get_imdb_rating(movies)).compare())

            if comparator == 'runtime':
                print(CompareNumeric(repo.get_runtime(movies)).compare())
            
            if comparator == 'box_office':
                print(CompareNumeric(repo.get_box_office(movies)).compare())
    
            if comparator == 'awards':
                print(CompareAwards(repo.get_awards(movies)).compare())

if __name__ == '__main__':
    Main().main()
