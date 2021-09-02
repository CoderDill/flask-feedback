from flask import Flask, render_template, redirect, session, flash, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "coolbeans"
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


@app.route("/users/<string:username>")
def user_detail(username):
    """Example hidden page for logged-in users only."""
    user = User.query.filter_by(username=username).first()

    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/")
    else:
        return render_template("user_detail.html", user=user)


@app.route("/logout")
def logout():
    """Logs user out and redirects to homepage."""

    session.pop("username")

    return redirect("/")


@app.route("/users/<string:username>/delete", methods=['POST'])
def delete_user(username):
    """Delete User"""

    session.pop("username")
    user = User.query.filter_by(username=username).first()
    db.session.delete(user)
    db.session.commit()

    return redirect("/")


@app.route("/feedback/<int:id>/delete", methods=["POST"])
def delete_feedback(id):
    feedback = Feedback.query.get_or_404(id)
    db.session.delete(feedback)
    db.session.commit()
    return redirect(f"/users/{feedback.username}")

@app.route("/users/<string:username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    form = 
    return render_template("feedback_form.html")