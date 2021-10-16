from flask import \
    Blueprint, flash, redirect, render_template, request, url_for
from flask_login import \
    current_user, login_required, login_user, logout_user
from sqlalchemy import desc

from flask_blog import db, bcrypt
from flask_blog.models import User, Post
from flask_blog.users.forms import \
    LoginForm, RegistrationForm, ResetPasswordForm, \
    RequestResetForm, UpdateAccountForm
from flask_blog.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)


# register page (something.domain/register)
@users.route("/register", methods=['get', 'post'])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))
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
        return redirect(url_for('main.home_page'))
    return render_template('register.html', title='Register', form=form)


# login page (something.domain/login)
@users.route("/login", methods=["get", "post"])
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home_page'))
        else:
            flash('Invalid login nerd! Check email and password', 'danger')
    return render_template('login.html', title='login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home_page'))


@users.route('/account', methods=["get", "post"])
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
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account',
                           image=image_file, form=form)


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query \
        .filter_by(author=user).order_by(desc(Post.date_posted)) \
        .paginate(page=page, per_page=2)
    return render_template("user_posts.html", posts=posts, user=user)


@users.route("/reset_password", methods=['get', 'post'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent to your account. '
              + 'Follow the link provided to reset your password', 'info')
        return redirect(url_for('users.login_page'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['get', 'post'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))
    user = User.verify_reset_token(token)
    if not user:
        flash('This token is invalid or expired.', 'warning')
        return redirect(url_for("users.reset_request"))
    else:
        form = ResetPasswordForm()
        if form.validate_on_submit():
            hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user.password = hashed
            db.session.commit()
            flash(f'Your account has been created you can now log in!', 'success')
            return redirect(url_for('main.home_page'))
        return render_template('reset_password.html', title='Reset Password', form=form)
