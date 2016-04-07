# Store some const number and common function.
from MySQLdb import cursors

import MySQLdb

MAX_ITEM_COUNT_PER_PAGE = 10
MAX_INTEGER_VALUE = 9999999
DATA_LOCATION_PREFIX = 'data/small/'
DATA_LOCATION_MOVIE = DATA_LOCATION_PREFIX + 'movies.csv'
DATA_LOCATION_LINKS = DATA_LOCATION_PREFIX + 'links.csv'
DATA_LOCATION_RATINGS = DATA_LOCATION_PREFIX + 'ratings.csv'
DATA_LOCATION_TAGS = DATA_LOCATION_PREFIX + 'tags.csv'

# Get the paging index.
# The input is current index and total page count.
# The output is start index, current index, and last index.
# eg:
#  -For input (3, 100), return (1, 3, 10)
#  -For input (10, 100), return (5, 10, 14)
#  -For input (4, 7), return (1, 4, 7)
# It simply try all possible start/end index combination, then filter and choose the best one.
def get_start_end_index(current_index, total_page_count):
    actual_page_count = min(10, total_page_count)
    diff = MAX_INTEGER_VALUE
    min_position = MAX_INTEGER_VALUE

    # Try all possible position of current index.
    for i in range(0, actual_page_count):
        # Calculate the corresponding start/end index
        min_index = current_index - i
        max_index = current_index + actual_page_count - i - 1

        # Filter invalid start/end index.
        if min_index <= 0:
            continue
        if max_index > total_page_count:
            continue

        # Choose the best start/end index:
        # Rule:
        #  -Difference of first half and second half should be small.
        #  -If the difference are the same, choose the smaller start index.
        current_diff = abs((current_index - min_index) - (max_index - current_index))
        if current_diff < diff:
            diff = current_diff
            min_position = min_index
        if current_diff == diff:
            if min_position > min_index:
                min_position = min_index

    # Error handle: current index out of range.
    if min_position == MAX_INTEGER_VALUE:
        return (current_index, current_index, current_index)

    return (min_position, current_index, min_position + actual_page_count - 1)


# Create a mysql DB connection
def create_db_connection(host, port, user, passwd, db):
    ret = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db)
    ret.autocommit(True)
    return ret

# Check if the data are all digits, or empty string
def valid_numbers(data):
    for i in data:
        if i not in '0123456789.':
            return False

    return True

# Join all elements in a string by comma
def convert_set_to_string(s):
    if s == None:
        return None
    return ','.join(s)

# Extract title and year from the raw title
# Sample raw title:
#    Toy Story (1995)
def parse_title(data):
    title = data.strip()[ : -6].strip()
    year = data.strip()[-5 : -1]

    if valid_numbers(year):
        return (title, year)

    return None