# YOU NEED TO PIP INSTALL ALL OF THESE
# pip install flask
# pip install flask-wtf
# pip install flask-sqlalchemy
# pip install flask-bcrypt
# pip install flask-login
# pip install Pillow
# you may need:
# pip install email_validator
from flask_blog import app
if __name__ == '__main__':
    app.run(debug=True)
