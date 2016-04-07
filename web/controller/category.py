from flask import Blueprint, render_template, redirect

import model.db_model as model
import util.util as util

# Category page handler
mod = Blueprint('category', __name__)

# Redirect the first page, add the default index 0
@mod.route('/category/<category_name>')
def category_1st_page(category_name):
    return redirect('/category/' + category_name + '/0')

# Handle category browsing page.
@mod.route('/category/<category_name>/<page_index>')
def category(category_name, page_index):
    # Pull film data from DB.
    res = model.get_film_by_category(category_name, page_index)
    film_list = res[0]
    total_page_number = res[1]

    # Calculate start/end index for navigation bar.
    page_index_tuple = util.get_start_end_index(int(page_index) + 1, int(total_page_number) + 1)

    # Render the template.
    return render_template('category.html', \
        category_name = category_name, \
        # List of page indexes before current index.
        page_index_before_list = range(page_index_tuple[0] - 1, page_index_tuple[1] - 1),
        current_page_index = int(page_index),
        # List of page indexes before current index.
        page_index_after_list = range(page_index_tuple[1], page_index_tuple[2]),
        # Parameter for template navigation_bar
        url_prefix = '/category/' + category_name,
        film_list = film_list)

