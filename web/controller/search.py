from flask import Blueprint, render_template, redirect, request

import model.db_model as model
import util.util as util

# Search page handler
mod = Blueprint('search', __name__)

# Extract the keyword parameter and redirect the post request to get request.
@mod.route('/search', methods=['POST'])
def post_search():
    keyword = request.form["keyword"].encode('utf-8')
    return redirect('/search/' + keyword)

# Redirect the first page, add the default index 0
@mod.route('/search/<keyword>')
def search_1st_page(keyword):
    return redirect('/search/' + keyword + '/0')

# Handle search page.
@mod.route('/search/<keyword>/<page_index>')
def search(keyword, page_index):
    # Pull film data from DB.
    res = model.search_film_by_keyword(keyword, page_index)
    film_list = res[0]
    total_page_number = res[1]

    # Calculate the start/end index.
    page_index_tuple = util.get_start_end_index(int(page_index) + 1, int(total_page_number) + 1)

    # Render the page.
    return render_template('search.html', \
        keyword = keyword, \
        page_index_before_list = range(page_index_tuple[0] - 1, page_index_tuple[1] - 1),
        current_page_index = int(page_index),
        page_index_after_list = range(page_index_tuple[1], page_index_tuple[2]),
        url_prefix = '/search/' + keyword,
        film_list = film_list)