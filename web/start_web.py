from flask import Flask

import controller.home as home
import controller.film as film
import controller.search as search
import controller.category as category

# Load the modules and start the web server.  Listening on port 30000
app = Flask(__name__)

app.register_blueprint(home.mod)
app.register_blueprint(film.mod)
app.register_blueprint(search.mod)
app.register_blueprint(category.mod)

app.run(host='0.0.0.0', port=30000, debug=True)