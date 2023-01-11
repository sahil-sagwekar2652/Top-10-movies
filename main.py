from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField
from wtforms.validators import DataRequired, NumberRange
import requests

TMDB_API_KEY = "be9b8d852a023e388f97cead7ca8561e"
TMDB_IMG_ENDPOINT = "https://image.tmdb.org/t/p/w600_and_h900_bestv2"
TMDB_SEARCH_ENDPOINT = "https://image.tmdb.org/t/p/w600_and_h900_bestv2"

app = Flask(__name__)
# WTForms
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
# SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///top-movies-collection.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.app_context().push()


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.String(4), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(500))  # , nullable=False)
    img_url = db.Column(db.String(500), nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Book {self.title}>'


db.create_all()


class AddMovieForm(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired(message="This field can't be empty.")])
    submit = SubmitField(label='Submit')


class EditMovieForm(FlaskForm):
    rating = DecimalField(label='Your rating out of 10 e.g. 8.5',
                          places=1,
                          validators=[DataRequired(message="This field can't be empty."),
                                      NumberRange(min=0.0, max=10.0, message="Rating must be between 0.0 to 10.0")])
    review = StringField(label='Your review')      # , validators=[DataRequired(message="This field can't be empty.")])
    submit = SubmitField(label='Done')


@app.route("/")
def home():
    # all_movies = db.session.query(Movie).all()
    all_movies = Movie.query.order_by(Movie.rating.desc()).all()
    return render_template("index.html", movies_data=all_movies)


@app.route("/add", methods=['POST', 'GET'])
def add():
    form = AddMovieForm()

    if form.validate_on_submit():
        print("True")
        params = {"query": form.title.data,
                  "api_key": TMDB_API_KEY}

        response = requests.get(url=f"https://api.themoviedb.org/3/search/movie?", params=params)
        data = response.json()['results'][0]

        print(data['original_title'])
        print(data['release_date'])
        print(data['overview'])
        print(data['vote_average'])
        new_movie = Movie(
            title=data['original_title'],
            year=data['release_date'][:4],
            description=data['overview'],
            rating=data['vote_average'],
            ranking=0.0,
            review="",
            img_url=f"{TMDB_IMG_ENDPOINT}{data['poster_path']}"
        )

        db.session.add(new_movie)
        db.session.commit()

        return redirect(url_for('update', movie_title=data['original_title']))

    return render_template('add.html', form=form)


@app.route("/update/<movie_title>", methods=['POST', 'GET'])
def update(movie_title):
    form = EditMovieForm()

    if form.validate_on_submit():
        selected_movie = Movie.query.filter_by(title=movie_title).first()

        selected_movie.rating = form.rating.data
        if form.review.data != "":
            selected_movie.review = form.review.data
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('edit.html', form=form, m_title=movie_title)


@app.route("/delete/<movie_id>")
def delete(movie_id):
    selected_movie = Movie.query.get(movie_id)
    db.session.delete(selected_movie)
    db.session.commit()

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
