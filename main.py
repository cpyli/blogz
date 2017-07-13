from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:helloworld@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'hewrcqnu328832432#@$2'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(720))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner_id):
        self.title = title
        self.body = body
        self.owner_id = owner_id

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password

def is_blog_valid(user_input):
    if user_input != "":
        return True
    else:
        return False

def is_username_password_valid(user_input):
    if len(user_input) > 2 and len(user_input) < 21:
        if " " not in user_input:
            return True
    else:
        return False

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            flash('Logged in')
            print(session)
            return redirect('/newpost')

        elif user and user.password != password:
            flash('User password is incorrect')
            return redirect('/login')

        else:
            flash('Username does not exist')
            return redirect('/login')

    else:
        return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ""
        password_error = ""
        verify_error = ""

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash('Username already exists')
            return render_template('/signup.html', 
            username=username, password="", verify="")

        else:
            if not is_username_password_valid(username):
                username_error = "Not a valid username. Must be 3 to 20 characters long and contain no spaces."

            if not is_username_password_valid(password):   
                password_error = "Not a valid password. Must be 3 to 20 characters long and contain no spaces."
                password = ""

            if not is_username_password_valid(verify):   
                verify_error = "Not a valid password. Must be 3 to 20 characters long and contain no spaces."
                verify = ""

            if not password_error and not verify_error:
                if password != verify:        
                    password_error = "Passwords did not match. Must be 3 to 20 characters long and contain no spaces."        
                    verify_error = "Passwords did not match. Must be 3 to 20 characters long and contain no spaces."
                    password = ""
                    verify = ""

            if not username_error and not password_error and not verify_error:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                flash('Logged in')
                print(session)
                return redirect('/newpost')

            else:
                return render_template('/signup.html', username=username, password="",
                verify="", username_error=username_error, password_error=password_error,
                verify_error=verify_error)

    return render_template('signup.html')

@app.route('/newpost', methods=['GET','POST'])
def newpost():
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        entry_title = request.form['title']
        entry_body = request.form['body']

        title_error = ""
        body_error = ""

        if not is_blog_valid(entry_title):
            title_error = "Enter blog title"
    
        if not is_blog_valid(entry_body):
            body_error = "Enter blog content"

        if not title_error and not body_error:
            new_entry = Blog(entry_title, entry_body, owner.id)
            db.session.add(new_entry)
            db.session.commit()   

            new_entry_id = str(new_entry.id)
            new_entry_URL = '/entry?id=' + new_entry_id

            return redirect(new_entry_URL)
        
        else:
            return render_template('newpost.html', 
            entry_title=entry_title, entry_body=entry_body,
            title_error=title_error, body_error=body_error,
            title="Add a Blog Post!")

    else:
        return render_template('newpost.html', title="Add a Blog Post!")

@app.route('/entry', methods=['GET', 'POST'])
def entry(): 
    id = request.args.get('id')
    entry = Blog.query.get(id)
    title = entry.title
    return render_template('entry.html', title=title, entry=entry)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()

    return render_template('index.html', title="List of Blog Users", users=users)

@app.route('/blog', methods=['GET','POST'])
def blog():   

    user_id = request.args.get('user_id')
    entry_id = request.args.get('entry_id')

    if user_id:
        user = User.query.get(user_id)
        entries = Blog.query.filter_by(owner_id=user.id).all()
        return render_template('singleuser.html', title="User Blog Posts", user=user, entries=entries)

    elif entry_id:
        entry = Blog.query.get(entry_id)
        title = entry.title
        return render_template('entry.html', title=title, entry=entry)

    else:
        entries = Blog.query.all()
        return render_template('blog.html', title="All Blog Posts", entries=entries)

if __name__ == '__main__':
    app.run()