from flask import Flask ,render_template,request,render_template,redirect,session,flash
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO']= True
db=SQLAlchemy(app)
app.secret_key = 'y337kgcy&4b'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(120),unique = True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self,email,password):
        self.email = email
        self.password = password
        


class Blog(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    blog_title = db.Column(db.String(120))
    blog_body = db.Column(db.Text(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,blog_title,blog_body,owner):
        self.blog_title = blog_title
        self.blog_body = blog_body
        self.owner=owner      


@app.route('/', methods=['POST','GET'])
def index():  
    owners = User.query.all() 
    return render_template('home.html',users=owners)


@app.route('/allposts', methods=['POST','GET'])
def home():
    owners = User.query.all()
    blogs = Blog.query.all()
    return render_template('allposts.html', title="Users!",
                        blogs = blogs,users = owners)


@app.route('/blog', methods=['POST','GET'])

def single_blog():
    blog_id = request.args.get('id')
    blog_user = request.args.get('user')
    if blog_id:
        blog_id=int(blog_id)
        blog=Blog.query.get(blog_id)
        ownerid = blog.owner_id
        owner = User.query.filter_by(id = ownerid).first()
        email=owner.email

        return render_template('singlepost.html',blog_title=blog.blog_title,blog_body=blog.blog_body,user=email)
    elif blog_user:
        email = request.args.get('user')
        owner = User.query.filter_by(email = email).first()
        id = owner.id
        blogs = Blog.query.filter_by(owner_id = id).all()
        if email in session:
            email=session['email']
        return render_template('blog.html', title="Blog Posts!",
                            blogs = blogs,user = email)
        

@app.route("/login", methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = User.query.filter_by(email=email)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['email'] = user.email
                flash('welcome back, '+user.email)
                return redirect("/newpost")
        flash('bad username or password')
        return redirect("/login")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        if not is_email(email):
            flash('zoiks! "' + email + '" does not seem like an email address')
            return redirect('/register')
        email_db_count = User.query.filter_by(email=email).count()
        if email_db_count > 0:
            flash('yikes! "' + email + '" is already taken and password reminders are not implemented')
            return redirect('/register')
        if password != verify:
            flash('passwords did not match')
            return redirect('/register')
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        session['email'] = user.email
        return redirect("/newpost")
    else:
        return render_template('register.html')

def is_email(string):
    # for our purposes, an email string has an '@' followed by a '.'
    # there is an embedded language called 'regular expression' that would crunch this implementation down
    # to a one-liner, but we'll keep it simple:
    atsign_index = string.find('@')
    atsign_present = atsign_index >= 0
    if not atsign_present:
        return False
    else:
        domain_dot_index = string.find('.', atsign_index)
        domain_dot_present = domain_dot_index >= 0
        return domain_dot_present

@app.route("/logout", methods=['POST','GET'])
def logout():
    if 'email' in session:
        del session['email']
    return redirect("/")


@app.route('/newpost', methods=['POST','GET'])

def add_blog():
    titleerror=''
    bodyerror=''
    
    if request.method == 'POST':

        title = request.form['blog_title']
        body = request.form['blog_body']
        if title == "" or body == "":
            titleerror = 'title field is empty'
            bodyerror = 'Body is empty'
            return render_template('newpost.html',title_error=titleerror,body_error=bodyerror)
        elif title == "" :
            titleerror = 'title field is empty'

            return render_template('newpost.html',title_error=titleerror,body_error=bodyerror)
        elif  body == "":
            bodyerror = 'Body is empty'
            return render_template('newpost.html',title_error=titleerror,body_error=bodyerror)
        
        else:  
            
            owner = User.query.filter_by(email=session['email']).first()   
            db.session.add(Blog(title,body,owner))
            db.session.commit()
            email = session['email']
            return render_template('singlepost.html',blog_title=title,blog_body=body,user = email)
            
    
    return render_template('newpost.html',Title="New Blog")
    

if __name__ == "__main__":
    app.run()