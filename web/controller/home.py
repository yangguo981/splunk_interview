from flask import Blueprint, render_template
import model.db_model as model

# Home page handler
mod = Blueprint('home', __name__, url_prefix='/')

# handle home page .
@mod.route('/')
def home():
    return render_template('home.html', \
        film_list = model.get_home_page_film_list(), \
        category_list = model.get_category_list())