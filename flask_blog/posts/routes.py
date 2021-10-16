from flask import abort, Blueprint, flash, render_template, url_for, \
    redirect, request
from flask_login import current_user, login_required

from flask_blog import db
from flask_blog.models import Post
from flask_blog.posts.forms import PostForm

posts = Blueprint('posts', __name__)


@posts.route('/post/new', methods=["get", "post"])
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
        return redirect(url_for('main.home_page'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@posts.route("/post/<int:post_id>")
def post(post_id):
    this_post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=this_post.title, post=this_post)


@posts.route("/post/<int:post_id>/update", methods=['get', 'post'])
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
        return redirect(url_for('posts.post', post_id=this_post.id))
    elif request.method == 'GET':
        form.title.data = this_post.title
        form.content.data = this_post.content
    return render_template('create_post.html', title="Update Post",
                           form=form, legend='Update Post', post_id=this_post.id)


@posts.route("/post/<int:post_id>/delete_post", methods=['post'])
@login_required
def delete_post(post_id):
    this_post = Post.query.get_or_404(post_id)
    if this_post.author != current_user:
        abort(403)
    db.session.delete(this_post)
    db.session.commit()
    flash('Your post has been deleted.', 'danger')
    return redirect(url_for('main.home_page'))
