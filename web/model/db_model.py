from MySQLdb import cursors
from sets import Set

import MySQLdb
import json
import util.util as util

# Data model to connect with DB
conn = util.create_db_connection('localhost', 3306, 'root', 'root', 'test')
cur = conn.cursor()

# Get home page film list
# Randomly select 10 films with rating >= 4
def get_home_page_film_list():
    return __execute_query(("SELECT * FROM movie WHERE rating >= 4 ORDER BY RAND() limit 10"))

# Get film details by movie_id
def get_film_by_id(movie_id):
    return __execute_query(("SELECT * FROM movie WHERE movie_id = " + movie_id))[0]

# Get film by keyword match.
def search_film_by_keyword(keyword, page_index):
    return __get_film_by_feature('title', keyword, page_index)

# Get film by category match.
def get_film_by_category(category, page_index):
    return __get_film_by_feature('genres', category, page_index)

# Get all categories
def get_category_list():
    query = ("SELECT DISTINCT genres AS gen FROM movie")
    cur.execute(query)
    ret = Set([])
    for result in cur:
        for i in result[0].split('|'):
            ret.add('"' + i + '"')
    return json.loads('[' + ','.join(ret) + ']')

# Help function, query feature_name field by feature_value.
def __get_film_by_feature(feature_name, feature_value, page_index):
    # Get film count match this query. Used for paging.
    total_count = __get_film_count_by_query(("SELECT COUNT(*) FROM movie WHERE " + \
        feature_name + " LIKE '%" + feature_value + "%'"))
    total_page_number = int(total_count) / util.MAX_ITEM_COUNT_PER_PAGE

    # Use LIMIT to do paging.
    return (__execute_query(("SELECT * FROM movie WHERE " + feature_name +  " LIKE '%" + \
        feature_value + "%' ORDER BY rating DESC LIMIT " + \
        str(int(page_index) * util.MAX_ITEM_COUNT_PER_PAGE) + ', ' + \
        str(util.MAX_ITEM_COUNT_PER_PAGE))), total_page_number)

# Compose JSON format output from SQL query result.
def __parse_json_from_sql(cur):
    # Add the open '[' for json.
    res = '['

    # Extract all field names.
    field_names = [i[0] for i in cur.description]

    # Iterator over query result, compose the single json element and append to the final output.
    for result in cur:
        tmp = []
        idx = 0
        for item in result:
            tmp.append('"' + field_names[idx] + '"' + ':"'+ str(item).replace('"', '') + '"')
            idx = idx + 1
        res = res + '{' + ','.join(tmp) + '},'

    # Strip the last ',' and append the close ']'
    res = res[:-1] + ']'

    # Error handle, if the query result is empty.
    if res == ']':
        return ''

    return json.loads(res)

# Execute the SQL query, convert the result to JSON.
def __execute_query(query):
    cur.execute(query)
    return __parse_json_from_sql(cur)

# Execute the SQL query and convert to count
def __get_film_count_by_query(query):
    cur.execute(query)
    return cur.fetchone()[0]