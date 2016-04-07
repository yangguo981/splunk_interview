from flask import Blueprint, render_template

import model.db_model as model

# Film details page handler
mod = Blueprint('film', __name__)

# Handle film details page.
@mod.route('/film/<film_id>')
def film(film_id):
    return render_template('film.html', film_info = model.get_film_by_id(film_id))