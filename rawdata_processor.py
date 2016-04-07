import csv
from sets import Set
import MySQLdb
from MySQLdb import cursors
import web.util.util as util

# Parse and load data from movie.csv
# Return an object.
def load_movie_metadata():
    movies_metadata = {}
    idx = 0
    with open(util.DATA_LOCATION_MOVIE, 'r') as c:
        reader = csv.reader(c, delimiter=',', quotechar='"')

        # skip the headers
        next(reader, None)

        idx = 0
        for row in reader:
            idx = idx + 1
            if len(row) != 3:
                print 'Error processing movie row: ', idx, 'Code: 0'
                print row
            movie_id = row[0]
            parsed_title = util.parse_title(row[1])
            if parsed_title == None:
                print 'Error processing movie row: ', idx, 'Code: 1'
                print row
                continue
            title = parsed_title[0]
            year = parsed_title[1]
            genres = row[2]

            # Add one entry.
            movies_metadata[movie_id] = {'title': title, 'year': year, 'genres': genres}

    return movies_metadata

# Load links information and append to object.
def load_and_append_links(movie_metadata):
    with open(util.DATA_LOCATION_LINKS, 'r') as c:
        reader = csv.reader(c, delimiter=',', quotechar='"')

        # skip the headers
        next(reader, None)

        idx = 0
        for row in reader:
            idx = idx + 1
            if len(row) != 3:
                print 'Error processing links row:', idx, 'Code: 0'
                print row
                continue
            movie_id = row[0]
            imdb_id = row[1]
            tmdb_id = row[2]
            if util.valid_numbers(movie_id) == False or util.valid_numbers(imdb_id) == False or \
                util.valid_numbers(tmdb_id) == False:
                print 'Error processing links row:', idx, 'Code: 1'
                print row
                continue

            if movie_id not in movie_metadata:
                print 'Error processing links row:', idx, 'Code: 2'
                print row
                continue

            # Append imdb/tmdb data into object.
            value = movie_metadata[movie_id]
            value['imdb'] = imdb_id
            value['tmdb'] = tmdb_id
            movie_metadata[movie_id] = value

    return movie_metadata

# Load rating information, calculate average rating and append to object.
def load_and_calculate_rating(movie_metadata):
    with open(util.DATA_LOCATION_RATINGS, 'r') as c:
        reader = csv.reader(c, delimiter=',', quotechar='"')

        # skip the headers
        next(reader, None)

        idx = 0
        for row in reader:
            idx = idx + 1
            if len(row) != 4:
                print 'Error processing ratings row:', idx, 'Code: 0'
                print row
                continue
            movie_id = row[1]
            rating = row[2]
            if util.valid_numbers(movie_id) == False or util.valid_numbers(rating) == False:
                print 'Error processing rating row:', idx, 'Code: 1'
                print row
                continue

            if movie_id not in movie_metadata:
                print 'Error processing rating row:', idx, 'Code: 2'
                print row
                continue

            value = movie_metadata[movie_id]
            if 'user_count' not in value:
                value['user_count'] = 0
            if 'rating' not in value:
                value['rating'] = 0

            # Sum up total rating/user count.
            value['user_count'] = value['user_count'] + 1
            value['rating'] = value['rating'] + float(rating)
            movie_metadata[movie_id] = value

    # Calculate average rating information for each entry, and keep a list of movie which doesn't
    # have rating information.
    key_to_remove = []
    for key, value in movie_metadata.iteritems():
        if 'rating' not in value or 'user_count' not in value:
            print 'Rating information missed for movie:',key
            key_to_remove.append(key)
            continue

        # Calculate average rating and update object.
        average_rating = value['rating'] / value['user_count']
        value.pop('rating')
        value['average_rating'] = average_rating
        movie_metadata[key] = value

    # Remove movie without rating information.
    for key in key_to_remove:
        movie_metadata.pop(key)

    return movie_metadata

# Load tags information and update object.
def load_and_append_tags(movie_metadata):
    with open(util.DATA_LOCATION_TAGS, 'r') as c:
        reader = csv.reader(c, delimiter=',', quotechar='"')

        # skip the headers
        next(reader, None)

        idx = 0
        for row in reader:
            idx = idx + 1
            if len(row) != 4:
                print 'Error processing tags row:', idx, 'Code: 0'
                print row
                continue
            movie_id = row[1]
            tag = row[2].strip().lower()

            if util.valid_numbers(movie_id) == False:
                print 'Error processing tags row:', idx, 'Code: 1'
                print row
                continue

            if movie_id not in movie_metadata:
                print 'Error processing tags row:', idx, 'Code: 2'
                print row
                continue

            value = movie_metadata[movie_id]
            if 'tags' not in value:
                value['tags'] = Set()
            value['tags'].add(tag)
            movie_metadata[movie_id] = value

    return movie_metadata

# Append all information together into the final object.
def append_other_metadata(movie_metadata):
    movie_metadata = load_and_append_links(movie_metadata)
    movie_metadata = load_and_calculate_rating(movie_metadata)
    movie_metadata = load_and_append_tags(movie_metadata)
    return movie_metadata

# Load the raw data and insert into DB.
if __name__ == "__main__":
    # Create DB connection and the insert query template.
    conn = util.create_db_connection('localhost', 3306, 'root', 'root', 'test')
    cur = conn.cursor()
    insert = 'INSERT INTO movie(movie_id, title, genres, year, rating, imdb, tmdb, \
        tags, related_films, user_count) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    params = []
    cache_size = 0

    # Iterator over all extracted movie metadata information and insert into DB.
    for movie_id, value in append_other_metadata(load_movie_metadata()).iteritems():
        title = value['title']
        genres = value['genres']
        year = value['year']
        rating = value['average_rating']
        imdb = value['imdb']
        tmdb = value['tmdb']
        tags = None
        if 'tags' in value:
            tags = util.convert_set_to_string(value['tags'])
        user_count = value['user_count']
        # Placeholder for related films.
        related_films = None
        cache_size = cache_size + 1
        params.append((movie_id, title, genres, year, rating, imdb, tmdb, tags, \
            related_films, user_count))

        # Batch insert to DB.
        if cache_size == 50:
            try:
                cur.executemany(insert, params)
                params = []
                cache_size = 0
            except MySQLdb.Error, e:
                print params
                print 'Error',e

    # Insert the last couple of entries.
    try:
        cur.executemany(insert, params)
        params = []
        cache_size = 0
    except MySQLdb.Error, e:
        print params
        print 'Error',e

    cur.close()
    conn.close()