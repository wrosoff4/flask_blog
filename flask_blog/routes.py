import os
import secrets

from PIL import Image
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import desc

from flask_blog import app, db, bcrypt
from flask_blog.config import base_dir
from flask_blog.forms import \
    RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flask_blog.models import User, Post


# home page (something.domain/; something.domain/home)
@app.route("/")
@app.route("/home")
def home_page():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(desc(Post.date_posted)) \
        .paginate(page=page, per_page=2)
    return render_template("home.html", posts=posts)


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query \
        .filter_by(author=user).order_by(desc(Post.date_posted)) \
        .paginate(page=page, per_page=2)
    return render_template("user_posts.html", posts=posts, user=user)


# about page (something.domain/about)
@app.route("/about")
def about_page():
    return render_template("about.html", title="About")


# register page (something.domain/register)
@app.route("/register", methods=['get', 'post'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.password = hashed
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created you can now log in!', 'success')
        return redirect(url_for('home_page'))
    return render_template('register.html', title='Register', form=form)


# login page (something.domain/login)
@app.route("/login", methods=["get", "post"])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home_page'))
        else:
            flash('Invalid login nerd! Check email and password', 'danger')
    return render_template('login.html', title='login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_page'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    pic_fn = random_hex + f_ext
    pic_path = os.path.join(base_dir, 'static/profile_pics', pic_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(pic_path)
    return pic_fn


@app.route('/account', methods=["get", "post"])
@login_required
def account():
    image_file = url_for('static', filename='profile_pics/'
                                            + current_user.image_file)
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            pic_file = save_picture(form.picture.data)
            current_user.image_file = pic_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account',
                           image=image_file, form=form)


@app.route('/post/new', methods=["get", "post"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        # create new post class to be added to db
        this_post = Post(title=form.title.data, content=form.content.data,
                         author=current_user)
        # add post to db
        db.session.add(this_post)
        # commit change to db
        db.session.commit()
        flash('Post Created', 'success')
        return redirect(url_for('home_page'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    this_post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=this_post.title, post=this_post)


@app.route("/post/<int:post_id>/update", methods=['get', 'post'])
@login_required
def update_post(post_id):
    this_post = Post.query.get_or_404(post_id)
    if this_post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        this_post.title = form.title.data
        this_post.content = form.content.data
        db.session.commit()
        flash('Your post has been update!', 'success')
        return redirect(url_for('post', post_id=this_post.id))
    elif request.method == 'GET':
        form.title.data = this_post.title
        form.content.data = this_post.content
    return render_template('create_post.html', title="Update Post",
                           form=form, legend='Update Post', post_id=this_post.id)


@app.route("/post/<int:post_id>/delete_post", methods=['post'])
@login_required
def delete_post(post_id):
    this_post = Post.query.get_or_404(post_id)
    if this_post.author != current_user:
        abort(403)
    db.session.delete(this_post)
    db.session.commit()
    flash('Your post has been deleted.', 'danger')
    return redirect(url_for('home_page'))
