from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegisterForm, EditProfile
from app.models import User
from datetime import datetime


@app.before_request
def last_seen():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    print(url_for('login'))
    return render_template("index.html", title="Home", posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.identify_password(form.password.data):
            flash("Invalid username or password.")
            return redirect(url_for('login'))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        login_user(user, remember=form.remember_me.data)
        return redirect(next_page)
    return render_template('login.html', title='Sign in', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.create_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Congrats! Registration successful!')
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html', title='Register', form=form)


@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts
    return render_template("profile.html", user=user, posts=posts, title="%s's Profile" % username)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfile()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("You changes have been saved.")
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title='Edit Profile', form=form)
