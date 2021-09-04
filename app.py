from flask import Flask, render_template, redirect, session, flash, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'thisissecret123')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route("/")
def homepage():
    """Show homepage"""

    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(
            username, password, email, first_name, last_name)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username already exists')
            return render_template('register.html', form=form)
        session['username'] = username
        flash('Welcome, Successfully Created Your Account!', "success")
        return redirect(f"/users/{username}")

    return render_template('register.html', form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login."""

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session["username"] = username
            return redirect(f"/users/{username}")

        else:
            form.username.errors = ["Please try again."]

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """Logs user out and redirects to homepage."""

    session.pop("username")

    return redirect("/")


@app.route("/users/<string:username>")
def user_detail(username):
    """Example hidden page for logged-in users only."""

    if "username" not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.filter_by(username=username).first()
    

    return render_template("user_detail.html", user=user)


@app.route("/users/<string:username>/delete", methods=["POST"])
def delete_user(username):
    """Delete User"""

    session.pop("username")
    user = User.query.filter_by(username=username).first()
    db.session.delete(user)
    db.session.commit()

    return redirect("/")


@app.route("/users/<string:username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)
        db.session.add(feedback)
        db.session.commit()
        return redirect(f"/users/{username}")
    else:
        return render_template("feedback_form.html", form=form)


@app.route(("/feedback/<int:feedback_id>/update"), methods=["GET", "POST"])
def update_feedback(feedback_id):

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = FeedbackForm(fb=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()
        return redirect(f"/users/{feedback.username}")
    return render_template("feedback_form.html", form=form, feedback=feedback)


@app.route("/feedback/<int:id>/delete", methods=["POST"])
def delete_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f"/users/{feedback.username}")
