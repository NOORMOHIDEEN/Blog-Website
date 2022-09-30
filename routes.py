

from flask_app import app,db,bcrypt
import secrets
import os
from PIL import Image
from flask import render_template,url_for,flash,redirect,request,abort
from flask_app.forms import RegistrationForm,LoginForm,UpdateAccountForm,PostForm
from flask_app.models import User,Post,Health
from flask_login import login_user,current_user,logout_user,login_required
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
import sys
from matplotlib.figure import Figure
@app.route("/")
@app.route("/home")
def home():    
    posts = Health.query.order_by(Health.date_posted.desc())     
    arr=[]
    for post in posts:
        bmi=post.weight/((post.height)*(post.height))
        bmi=round(float(bmi),2)
        arr.append(bmi)
    posts = Health.query.order_by(Health.date_posted.desc())
    return render_template('home.html',posts=posts,arr=arr)

@app.route("/about")
def about():    
    posts = Health.query.order_by(Health.date_posted.desc())     
    arr=[]
    for post in posts:
        bmi=post.weight/((post.height)*(post.height))
        arr.append(bmi)
    fig = Figure()
    ax = fig.subplots()
    ax.plot(arr)
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data1 = base64.b64encode(buf.getbuffer()).decode("ascii")
    return render_template('about.html',posts=posts,data1=data1)

@app.route("/about1")
def about1():    
    posts = Health.query.order_by(Health.date_posted.desc())     
    arr=[]
    for post in posts:
        
        arr.append(post.weight)
    fig = Figure()
    ax = fig.subplots()
    ax.plot(arr)
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # Embed the result in the html output.
    data1 = base64.b64encode(buf.getbuffer()).decode("ascii")
    return render_template('about.html',posts=posts,data1=data1)

@app.route("/register",methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_password= bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user=User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your Account has been created! You are now able to log in','success')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register',form=form)

@app.route("/login",methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form= LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user,remember=form.remember.data)
            next_page= request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password','danger')

    return render_template('login.html',title='Login',form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    _,f_ext=os.path.splitext(form_picture.filename)
    picture_fn= random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/profile_pics', picture_fn)
    output_size=(125,125)
    i=Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)   
    return picture_fn

@app.route("/account",methods=['GET','POST'])
@login_required
def account():
    form= UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file=save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data= current_user.username
        form.email.data = current_user.email
    image_file= url_for('static',filename='profile_pics/'+ current_user.image_file)
    return render_template('account.html',title='Account',image_file=image_file,form=form)

@app.route("/post/new",methods=['GET','POST'])
@login_required
def new_post():
    form= PostForm()
    if form.validate_on_submit():
        post= Health(week=form.week.data,height=form.height.data,weight=form.weight.data,bld_ps=form.bld_ps.data)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!','success')
        return redirect(url_for('home'))
    return render_template('create_post.html',title='Height Details',form=form,legend='Health Details')

@app.route("/post/<int:post_id>")
@login_required
def post(post_id):
    post=Post.query.get_or_404(post_id)
    return render_template('post.html',title=post.title,post=post)

@app.route("/post/<int:post_id>/update",methods=['GET','POST'])
@login_required
def update_post(post_id):
    post=Post.query.get_or_404(post_id)
    if post.author!= current_user:
        abort(403)
    form=PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been update!','success')
        return redirect(url_for('post',post_id=post.id))
    elif request.method == 'GET':        
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html',title='Update Post',form=form,legend='Update Post')

@app.route("/post/<int:post_id>/delete",methods=['POST'])
@login_required
def delete_post(post_id):
    post=Post.query.get_or_404(post_id)
    if post.author!= current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been Deleted!','success')
    return redirect(url_for('home'))
    
@app.route("/user/<string:username>")
def user_posts(username):
    page=request.args.get('page',1,type=int)
    user= User.query.filter_by(username=username).first_or_404()
    posts=Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page,per_page=5)
    return render_template('user_post.html',posts=posts,user=user)