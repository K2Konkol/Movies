from classes.Movie import Movie
from classes.HelperClasses import Highscore
from classes.DB import DB
import classes.Repository

FAKE_URL = 'http://fake_url'


def test_get_movie_no_apikey(mock_response):
    """Test that function returns an error if no API key is provided"""
    result = classes.Repository.get_movie(FAKE_URL, params=None)
    assert 'Error' in result


def test_get_movie_no_title(mock_response, auth):
    """Test that function returns an error if no movie title is provided"""
    result = classes.Repository.get_movie(FAKE_URL, params=auth)
    assert 'Error' in result


def test_get_movie(mock_response, auth):
    """Test that function returns JSON if parameters ok"""
    params = {"t": "Alien", "apikey": auth}
    result = classes.Repository.get_movie(FAKE_URL, params=params)
    print(result)
    assert 'Alien' in result['Title']


def test_get_apikey(auth):
    """Test that function returns apikey"""
    assert classes.Repository.get_apikey() == auth


def test_get_awards_no_oscar():
    data = "3 wins & 1 nomination."
    assert classes.HelperClasses.Parser.get_awards(None, data) == 3


def test_get_awards_oscar_nominated():
    data = "Nominated for 7 Oscars. Another 19 wins & 32 nominations."
    assert classes.HelperClasses.Parser.get_awards(None, data) == 19


def test_get_nominations():
    data = "Nominated for 7 Oscars. Another 19 wins & 32 nominations."
    assert classes.HelperClasses.Parser.get_nominations(None, data) == 32


def test_get_oscars_won():
    data = "Won 1 Oscar. Another 16 wins & 19 nominations."
    assert classes.HelperClasses.Parser.get_oscars(None, data) == 1


def test_parse_json_to_movie(mock_db_ok):
    response = mock_db_ok.json()
    alien = Movie.json_to_movie(response)
    assert alien.title == 'Alien'
    assert alien.director == 'Ridley Scott'
    assert alien.cast == 'Tom Skerritt, Sigourney Weaver, Veronica Cartwright, Harry Dean Stanton'
    assert alien.awards == 'Won 1 Oscar. Another 16 wins & 19 nominations.'


def test_db_empty(mock_db):
    db = DB.get_all_titles(mock_db)
    assert len(db.fetchall()) == 0


def test_insert_not_duplicated(mock_db):
    title = "Alien"
    DB.insert(mock_db, title)
    DB.insert(mock_db, title)
    db = DB.get_all_titles(mock_db)
    result = db.fetchall()
    assert len(result) == 1
    assert 'Alien' in str(result)


def test_update(mock_db):
    alien = Movie(
        title='Alien',
        awards='Won 1 Oscar. Another 16 wins & 19 nominations.'
    )
    DB.insert(mock_db, "Alien")
    DB.update(mock_db, alien)
    db = DB.get_by_title(mock_db, alien)
    result = db.fetchone()
    assert 'Alien' in str(result)
    assert 'Won 1 Oscar. Another 16 wins & 19 nominations.' in str(result)


def test_sort_by(mock_db_populated):
    db = DB.get_sorted_by(mock_db_populated, 'year')
    result = db.fetchall()
    assert len(result) == 5
    assert '2014' in str(result[0])
    assert '2000' in str(result[1])
    assert '1994' in str(result[2])
    assert '1994' in str(result[3])
    assert '1979' in str(result[4])


def test_filter_by_director(mock_db_populated):
    db = DB.get_filtered_by_director(mock_db_populated, 'Ridley Scott')
    result = db.fetchall()
    assert len(result) == 1
    assert 'Alien' in str(result)


def test_filter_by_actor(mock_db_populated):
    db = DB.get_filtered_by_actor(mock_db_populated, 'Sigourney Weaver')
    result = db.fetchall()
    assert len(result) == 1
    assert 'Alien' in str(result)


def test_filter_oscar_nominated(mock_db_populated):
    db = DB.get_oscar_nominated(mock_db_populated)
    result = db.fetchall()
    assert len(result) == 2
    assert 'Alien' not in str(result)
    assert 'Memento' in str(result)
    assert 'The Shawshank Redemption' in str(result)


def test_filter_boxoffice_over_hundred_million(mock_db_populated):
    db = DB.get_boxoffice_over_hundred_million(mock_db_populated)
    filtered = db.fetchall()
    assert len(filtered) == 1
    assert 'Alien' not in str(filtered)
    assert 'Forrest Gump' in str(filtered)


def test_filter_by_language(mock_db_populated):
    db = DB.get_by_language(mock_db_populated, 'Spanish')
    filtered = db.fetchall()
    assert len(filtered) == 1
    assert 'Alien' not in str(filtered)
    assert 'Boyhood' in str(filtered)


def test_get_imdb_rating(mock_db_populated):
    db = DB.get_imdb_rating(mock_db_populated, 'Alien', 'Forrest Gump')
    result = db.fetchall()
    assert len(result) == 2


def test_get_awards(mock_db_populated):
    db = DB.get_awards(mock_db_populated, 'Boyhood', 'Forrest Gump')
    result = db.fetchall()
    assert len(result) == 2
    assert 'Forrest Gump' in str(result)
    assert 'Boyhood' in str(result)


def test_get_runtime(mock_db_populated):
    db = DB.get_runtime(mock_db_populated, 'Boyhood', 'Forrest Gump')
    result = db.fetchall()
    assert len(result) == 2
    assert 'Forrest Gump' in str(result)
    assert 'Boyhood' in str(result)


def test_get_for_highscores(mock_db_populated):
    db = DB.get_for_highscores(mock_db_populated)
    result = db.fetchall()
    assert len(result) == 5
    assert 'Alien' in str(result)
    assert '165 min' in str(result)
    assert '$23,844,220' in str(result)
    assert 'Won 6 Oscars. Another 40 wins & 67 nominations.' in str(result)
    assert '9.3' in str(result)


def test_get_highest_runtime(mock_db_populated):
    db = DB.get_for_highscores(mock_db_populated)
    result = db.fetchall()
    winner = Highscore().get_highest_runtime(result)
    assert 'Boyhood' in str(winner)
    assert '165 min' in str(winner)


def test_get_highest_box_office(mock_db_populated):
    db = DB.get_for_highscores(mock_db_populated)
    result = db.fetchall()
    winner = Highscore().get_highest_box_office(result)
    assert 'Forrest Gump' in str(winner)
    assert '$330,000,000' in str(winner)


def test_get_most_oscars(mock_db_populated):
    db = DB.get_for_highscores(mock_db_populated)
    result = db.fetchall()
    winner = Highscore().get_oscars_highscore(result)
    assert 'Forrest Gump' in str(winner)
    assert '6' in str(winner)


def test_get_most_nominations(mock_db_populated):
    db = DB.get_for_highscores(mock_db_populated)
    result = db.fetchall()
    winner = Highscore().get_nominations_highscore(result)
    assert 'Boyhood' in str(winner)
    assert '209' in str(winner)


def test_get_most_awards(mock_db_populated):
    db = DB.get_for_highscores(mock_db_populated)
    result = db.fetchall()
    winner = Highscore().get_awards_highscore(result)
    assert 'Boyhood' in str(winner)
    assert '171' in str(winner)


def test_get_highest_imdb_rating(mock_db_populated):
    db = DB.get_for_highscores(mock_db_populated)
    result = db.fetchall()
    winner = Highscore().get_highest_imdb_rating(result)
    assert 'The Shawshank Redemption' in str(winner)
    assert '9.3' in str(winner)
