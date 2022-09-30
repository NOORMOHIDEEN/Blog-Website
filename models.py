from flask_app import db,login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username= db.Column(db.String(20),unique=True,nullable=False)
    email= db.Column(db.String(50),unique=True,nullable=False)
    image_file = db.Column(db.String(20),nullable=False,default='default.jpg')
    password = db.Column(db.String(60),nullable=False)
    posts=db.relationship('Post',backref='author',lazy=True)
    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer,primary_key=True)   
    title=db.Column(db.String(100),nullable=False)
    date_posted = db.Column(db.DateTime,nullable=False,default=datetime.utcnow()) 
    content = db.Column(db.Text,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"

class Health(db.Model):
    id = db.Column(db.Integer,primary_key=True)   
    week=db.Column(db.String,nullable=False)
    height= db.Column(db.String,nullable=False)
    weight= db.Column(db.String,nullable=False)
    bld_ps=db.Column(db.String(20),nullable=False)
    date_posted = db.Column(db.DateTime,nullable=False,default=datetime.utcnow()) 
    def _repr_(self):
        return f"Health('{self.height}',{self.weight}','{self.date_posted}')"
