from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import Feedback, connect_db, db, User
from forms import LoginForm, RegisterForm, FeedbackForm

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)

@app.route('/')
def redirect_to_register():
    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        db.session.commit()

        session['username'] = new_user.username
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect(f"/users/{new_user.username}")

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    """ Log in the user """
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}!", "primary")
            session['username'] = user.username
            return redirect(f"/users/{user.username}")
        else:
            flash('Invalid username/password')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_user():
    session.pop('username')
    flash("Goodbye!", "info")
    return redirect('/')


@app.route('/users/<username>')
def show_secret_route(username):
    if "username" not in session:
        flash("Please login first!")
        return redirect('/')

    user = User.query.get_or_404(session['username'])
    posts = Feedback.query.filter_by(username=username).all()

    return render_template("user_info.html", user=user, posts=posts)

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """ Delete a user """
    if "username" in session:
        user = User.query.get_or_404(session['username'])
        db.session.delete(user)
        db.session.commit()
        session.pop('username')
        flash("The user has been deleted")
        return redirect('/')
    
    flash("Please login first!", "danger")
    return redirect('/')
    


@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    """ Show the feedback form and add feedback """
    if "username" not in session:
        flash("Please login first!")
        return redirect('/')

    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        new_post = Feedback(title=title, content=content, username=username)
        db.session.add(new_post)
        db.session.commit()
        return redirect(f"/users/{username}")
    
    return render_template('feedback_form.html', form=form)

@app.route('/feedback/<post_id>/edit', methods=['GET', 'POST'])
def edit_feedback(post_id):
    """ Show the feedback form and add feedback """
    if "username" not in session:
        flash("Please login first!")
        return redirect('/')
    postid = int(post_id)
    post = Feedback.query.get_or_404(postid)
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        post.title = title
        post.content = content
        db.session.add(post)
        db.session.commit()
        return redirect(f"/users/{session['username']}")
    
    return render_template('feedback_form.html', form=form)

@app.route('/feedback/<post_id>/delete', methods=['POST'])
def delete_feedback_post(post_id):
    """ Deletes the selected feedback post"""
    if "username" not in session:
        flash("Please login first!")
        return redirect('/')
    postid = int(post_id)
    post = Feedback.query.get_or_404(postid)

    if post.username == session['username']:
        db.session.delete(post)
        db.session.commit()
        flash("Post was deleted")
        return redirect(f"/users/{session['username']}")
    
    flash("Could not delete post")
    return redirect(f"/users/{session['username']}")
