from datetime import datetime

from flask import current_app
from flask_login import UserMixin
from itsdangerous import SignatureExpired, BadSignature
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from flask_blog import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )


# started by creating class models (tables/entities) in this file to avoid dependency errors
# User Model (table/entity)
class User(db.Model, UserMixin):
    # create new column(field) in User table called id, set metadata to integer, assign primary key
    id = db.Column(db.Integer, primary_key=True)
    # create new column(field) called username, metadata to string
    # max column(field) length 20
    # must be unique, cannot be null (not optional)
    username = db.Column(db.String(20), unique=True, nullable=False)
    # create new column(field) called email, string metadata, max length 120, must be unique, not null
    email = db.Column(db.String(120), unique=True, nullable=False)
    # new column(field) called image_file, string metadata, not null, has default value
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    # new column(field) called password, string meta data
    # stores 60 character hashed value, NOT THE PLAIN TEXT PASSWORD
    password = db.Column(db.String(60), nullable=False)
    # create a 1:M relationship (why is it one to many? you tell me, jk i know)
    # backref is a special type of attribute defined by a relationship
    posts = db.relationship('Post', backref='author', lazy=True)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    def __repr__(self):
        return f"User('{self.username}, {self.email}, {self.image_file}')"

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod  # doesnt refer to self reference
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except BadSignature:
            return None
        except SignatureExpired:
            return None
        return User.query.get(user_id)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0


# create new Model (table/entity) called Posts
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # from datetime import datetime, your one comment
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    # SET A FOREIGN KEY, make that two
    # NOTE: 'user.id' user is not User
    # the call to 'Post in the relationship in User references the Post class
    # the call 'user.id' is referencing the table_name/column_name NOT the class User
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # i spoiled you with comments, you're lucky i think you are nice

    def __repr__(self):
        return f"Post({self.title}, {self.author})"

# -------------------------------------------------------------------------------------------
# when you have finished making User and Post, IN YOUR VIRTUAL ENVIRONMENT TERMINAL
# >>> python
# >>> from flask_blog import db
# System will scream some stuff at you, ignore that fool
# >>> db.create_all()
# should be NO response here just new line, and 'site.db' should appear in project directory
# >>> from flask_blog import User, Post
# again, the system dont want none of this, so it keeps quite and just a new line should appear
# NOW SYSTEM HAS A DATABASE CREATED, WITH TWO TABLES user AND post


# --------------------------------------------------------------------------------------------
# lets add a user!
# IN TERMINAL:
# >>> user_1 = User(username='hobo365', email='i@cup.com', password='password')
# NOTE: we did not assign anything to the id field, "but that was our primary key!"
# because it is the primary key the system will automatically generate an id for us
# we have a user instance, now lets add it to the db
# >>> db.session.add(user_1)
# despite calling add, our user is not in the user table yet
# .add() just adds to the changes that the system will make next time it commits changes
# >>> user_2 = User(username='ToBeHonest', email='terrence.notphilip@uncw.com', password='password')
# >>> db.session.add(user_2)
# AGAIN neither user has been added to the user table yet
# the system has only been alerted that there is stuff the add the next time it syncs
# >>> db.session.commit()
# .commit() pushes any changes added using .add() to the session since the last .commit()
# now BOTH users should be in database


# ---------------------------------------------------------------------------------------------
# Lets query the database!
# >>> User.query.all()
# hopefully this time the system doesnt yell at you but kindly gives you what you deserve
# NOTE: the query was returned in an array list
# Here are some more queries to try:
# >>> User.query.first()

# NOTE THESE THREE QUERIES SEEM THE SAME SINCE USERNAMES ARE UNIQUE
# BUT TAKE A LOOK AT THEIR RETURN VALUES/TYPES
# >>> User.query.filter_by(username='ToBeHonest')
# >>> User.query.filter_by(username='ToBeHonest').all()
# >>> User.query.filter_by(username='ToBeHonest').first()

# >>> user = User.query.filter_by(username='ToBeHonest').first()
# >>> user
# >>> user.id
# lets find a user with a specific id
# >>> user = User.query.get(2)
# >>> user
# coding is so much fun, just look at how far we've come, way back to only seeing a lame "Hello World"
# >>> user.posts

# --------------------------------------------------------------------------------------------------
# Lets add some posts!
# >>> user.id
# >>> post_1 = Post(title='Blog 1', content='First post content!', user_id=user.id)
# >>> user = User.query.first()
# >>> post_2 = Post(title='Blogger?', content='I hardly know her', user_id=user.id)
# >>> db.session.add(post_1)
# >>> db.session.add(post_2)
# >>> db.session.commit()
# >>> user.posts

# note the return value, an array list, python loves array lists
# >>> for post in user.posts:
# ...    print(post.title)
# ...
# we split our posts up so only one thing will get printed to the thing
# >>> post = Post.query.first()
# >>> post
# >>> post.user_id
# RECALL: in the relationship method call we defined author
# while 'post' table doesnt track an author field
# an attribute for author exists, due to the relationship
# >>> post.author

# ----------------------------------------------------------------------------------------------------
# >>> db.drop_all()
# >> User.query.all()
#  wow... oops, probably shouldn't have done that
# >>> db.create_all()
# >>> User.query.all()
# back to a fresh db w empty tables
