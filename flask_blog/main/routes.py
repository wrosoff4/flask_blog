from flask import Blueprint, render_template, request
from sqlalchemy import desc

from flask_blog.models import Post

main = Blueprint('main', __name__)


# home page (something.domain/; something.domain/home)
@main.route("/")
@main.route("/home")
def home_page():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(desc(Post.date_posted)) \
        .paginate(page=page, per_page=2)
    return render_template("home.html", posts=posts)


# about page (something.domain/about)
@main.route("/about")
def about_page():
    return render_template("about.html", title="About")
