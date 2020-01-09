Usage:

Use this option to download data from OMDb and populate your database. Movie titles should be provided in Your local database. Note that you have to provide your own API key and put it in apikey.json file

    python3 movies.py -p, --populate

Use this option to add movie title in your local database - it automatically makes a request to fetch data from OMDb, and updates data in local database if the request was succesful, rolls back the insert otherwise.

    python3 movies.py -a, -add 'Gran Torino'

Sort movies by given column name, available:
'title', 'year', 'runtime', 'genre', 'director', 'cast', 'writer', 'language', 'country', 'awards', 'imdb_rating', 'imdb_votes', 'box_office'

    python3 movies.py -s, --sort_by year

Filters movies by given column name
Available parameters:
director 'director' - to filter by Director
actor 'actor'       - to filter by Actor
nominated           - shows movies that was nominated for Oscar but did not win any.
awarded             - shows movies that won more than 80% of nominations
earned              - shows movies that earned more than 100,000,000 $
language 'language' - shows only movies in certain Language

    python3 movies.py -f, --filter_by actor 'Brad Pitt'

Compares two given movies by given column
Available parameters:
imdb_rating         - by IMDb Rating
box_office          - by box office earnings
awards              - by number of awards won
runtime             - by runtime

    python3 movies.py -c, --compare runtime 'Alien' 'Boyhood'

Shows current highscores in :
- Runtime
- Box office earnings
- Most awards won
- Most nominations
- Most Oscars
- Highest IMDB Rating

        python3 movies.py --highscores
