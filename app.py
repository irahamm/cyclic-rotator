from flask import Flask, render_template, redirect, request, url_for, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, UserMixin, logout_user, login_required, current_user
from utils import rotate, unify_doubles
from email_validator import validate_email, EmailNotValidError
from models import conn, cursor
import json
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
my_bcrypt = Bcrypt(app)
login_manager = LoginManager(app)


class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return None

    cursor.execute("SELECT username FROM Users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    if result:
        return User(user_id=user_id, username=result[0])
    return None


@app.route("/")
@app.route("/home")
def home():
    return render_template('homepage.html')


@app.route("/editor")
def editor_page():
    return render_template('html1.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # get the username and password the user has entered
        username = request.form['username']
        password = request.form['password']
        # perform checks
        errors = []
        # fetch the password for this username
        cursor.execute("SELECT password FROM Users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if not result:  # (this line does not exist)
            errors.append("Invalid username")
        else:
            stored_password = result[0]
            if not my_bcrypt.check_password_hash(stored_password, password):
                errors.append("Invalid password")

        if errors:
            for error in errors:
                flash(error)
            return render_template('login.html')

        # congrats the details the user inputed are correct
        cursor.execute("SELECT user_id, username FROM Users WHERE username = %s", (username,))
        result = cursor.fetchone()
        user_id, username = result[0], result[1]
        user = User(user_id=user_id, username=username)
        login_user(user)
        flash(message=f"You are now logged in as: {username}")

        return redirect(url_for('home'))

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # get the info the user has typed in
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # check for possible errors
        errors = []
        # username length
        if len(username) < 3 or len(username) > 20:
            errors.append("Username must be between 3 to 20 characters.")
        try:  # email validity
            validate_email(email)
        except EmailNotValidError:
            errors.append("Invalid email address.")
        if len(password) < 6 or len(password) > 18:   # password length
            errors.append("Password must be between 6 to 18 characters.")
        # username already exists
        cursor.execute("SELECT 1 FROM Users WHERE username = %s", (username,))
        if cursor.fetchone():
            errors.append("The username you entered is taken. Please use a different one.")
        # password already exists
        cursor.execute("SELECT 1 FROM Users WHERE email_address = %s", (email,))
        if cursor.fetchone():
            errors.append("This email is already associated with a different account, please use a different address")

        if errors:
            for error in errors:
                flash(error)
            return render_template('signup.html')

        # congrats, we have passed all tests
        # now it's time to add to the data-base
        # hash password
        password_hash = my_bcrypt.generate_password_hash(password).decode('utf-8')
        cursor.execute("""
            INSERT INTO Users (username, email_address, password)
            VALUES (%s, %s, %s)
        """, (
            username,
            email,
            password_hash
        ))

        conn.commit()

        flash(message=f"Welcome {username}! You've been successfully signed up to the website."
                      f"You can now login and save exercises.")
        return redirect(url_for('home'))

    return render_template('signup.html')


@app.route('/cyclic-rotated-entry', methods=['GET', 'POST'])
def cyclic_rotated_entry_page():
    if request.method == 'POST':  # if I am not wrong this is where it sends it
        if 'exercise_json' in request.form:
            data = request.form.get('exercise_json')
            exercise = json.loads(data)
            rotations = list(rotate(exercise))
            return render_template('cyclic-rotated-entry.html', rotations=rotations)
        if "stackData" in request.form:
            data = request.form.get("stackData")
            exercise = json.loads(data)
            exercise = unify_doubles(exercise)
            rotations = list(rotate(exercise))
            return render_template('cyclic-rotated-entry.html', rotations=rotations)
        if "rotations" in request.form:   # the case where the user wants to save an exercise to his account
            data = request.form.get("rotations")
            rotations = json.loads(data)
            og_ex = rotations[0]
            cursor.execute("""INSERT INTO UserExercises (exercise, user_id) VALUES (%s, %s)""",
                           (og_ex, current_user.id))
            conn.commit()
            flash("exercise added successfully!")
            return render_template('cyclic-rotated-entry.html', rotations=rotations)


@app.route('/logout')
def logout():
    logout_user()
    flash("You've been logged out.")
    return redirect(url_for('home'))


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@app.route('/user-exercises', methods=['GET', 'POST'])
@login_required
def user_exercises():
    # get the exercises (although we could have done this previously, when initing the user object)
    cursor.execute("""SELECT exercise, ex_id FROM UserExercises WHERE user_id = %s""", (current_user.id, ))
    data = cursor.fetchall()
    data = [(exercise, ex_id) for exercise, ex_id in data]
    return render_template('user_exercises.html', ex_data=data)


@app.route('/delete-exercise', methods=['POST'])
@login_required
def delete_exercise():
    if request.method == "POST":  # handles the case the user wants to delete an exercise
        data = request.form.get('exercise-to-del')
        ex_id = json.loads(data)
        cursor.execute("""DELETE FROM UserExercises WHERE ex_id = %s""", (ex_id,))
        conn.commit()

        return redirect(url_for('user_exercises'))


@app.route('/FAQ')
def FAQ_page():
    return render_template('FAQ.html')


if __name__ == "__main__":
    app.run()
