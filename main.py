from datetime import date, datetime
import os

from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship

from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm

# Init flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_KEY")
ckeditor = CKEditor(app)
Bootstrap5(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", 'sqlite:///posts.db')
db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

# Init gravatar
gravatar = Gravatar(
    app,
    size=100,
    rating='g',
    default='retro',
    force_default=False,
    force_lower=False,
    use_ssl=False,
    base_url=None
)


# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# CONFIGURE TABLES
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    # Create reference to the User object, the "blogs" refers to the posts property in the User class.
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="parent_post")


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")

    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    text = db.Column(db.Text, nullable=False)


with app.app_context():
    db.create_all()


# Creating database data
# with app.app_context():
#     new_user = User(
#         name="Kyrylo Yefremov",
#         email="admin@gmail.com",
#         password="123",
#     )
#     new_blog = BlogPost(
#         author_id=1,
#         title="Blog Post 1",
#         subtitle="The subtitle",
#         date=datetime.now(),
#         body="bla bla bla....",
#         img_url="https:img_url.com",
#         author=new_user
#     )
#     db.session.add(new_user)
#     db.session.add(new_blog)
#     db.session.commit()


# Decorator for not allowing access to pages where admin roots are required
def admin_only(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return abort(code=403)
        elif current_user.id != 1:
            return abort(code=403)
        return function(*args, **kwargs)

    return decorated_function


@app.route('/register', methods=["POST", "GET"])
def register():
    register_form = RegisterForm()

    if register_form.validate_on_submit():
        # If user is trying to register with an existing email
        if db.session.execute(db.select(User).where(User.email == register_form.email.data)).scalar() is not None:
            flash("You've signed up with this email, log in instead!")
            return redirect(url_for("login"))

        hashed_password = generate_password_hash(password=register_form.password.data,
                                                 method="pbkdf2:sha256",
                                                 salt_length=8)
        new_user = User(
            name=register_form.name.data,
            email=register_form.email.data,
            password=hashed_password,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        return redirect(url_for("get_all_posts"))
    else:
        return render_template("register.html", form=register_form)


@app.route('/login', methods=["POST", "GET"])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        email = login_form.email.data
        entered_user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        # If email exist in the database
        if entered_user is None:
            flash("That email does not exist, please try again.")
            return redirect(url_for("login"))

        # If entered password matches to stored into a database
        if entered_user.check_password(password=login_form.password.data):
            login_user(entered_user)
            return redirect(url_for("get_all_posts"))
        else:
            flash("Incorrect password, please try again.")
            return redirect(url_for("login"))

    return render_template("login.html", form=login_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    comment_form = CommentForm()

    # Add a comment
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Please log in to live comments on blog posts!")
            return redirect(url_for("login"))

        new_comment = Comment(
            text=comment_form.comment.data,
            comment_author=current_user,
            author_id=current_user.id,
            post_id=post_id,
            parent_post=requested_post,
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("show_post", post_id=post_id))

    all_comments = db.session.execute(db.select(Comment).where(Comment.post_id == post_id)).scalars().all()
    return render_template("post.html",
                           post=requested_post,
                           form=comment_form,
                           current_user=current_user,
                           comments=all_comments,
                           gravatar=gravatar)


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=False, port=5002)
