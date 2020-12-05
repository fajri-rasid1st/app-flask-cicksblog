from cicksblog import db, bcrypt
from cicksblog.models import User, Post
from cicksblog.users.utilities import save_pict, send_token_email
from cicksblog.users.forms import (
    RegistrationForm,
    LoginForm,
    UpdateForm,
    ResetRequestForm,
    ResetPasswordForm,
)
from flask import render_template, redirect, url_for, flash, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
import datetime


users = Blueprint("users", __name__)


@users.route("/registration", methods=["GET", "POST"])
def registration():
    # check if user is already login
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    regist_form = RegistrationForm()

    if regist_form.validate_on_submit():
        # hashed the password
        hashed_password = bcrypt.generate_password_hash(
            regist_form.password.data
        ).decode("utf-8")
        # instance UserModel
        user = User(
            username=regist_form.username.data,
            email=regist_form.email.data,
            phone_number=regist_form.phone_number.data,
            password=hashed_password,
        )
        # insert user to database
        db.session.add(user)
        db.session.commit()
        # make a flash message when registration successfully
        flash("Your account has been craeted!🤗", "success")
        # redirecting to login
        return redirect(url_for("users.login"))

    return render_template("registration.html", title="Registration", form=regist_form)


@users.route("/login", methods=["GET", "POST"])
def login():
    # check if user is already login
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    login_form = LoginForm()

    if login_form.validate_on_submit():
        # check user in database
        user = User.query.filter_by(username=login_form.username.data).first()
        # if user is found in database
        if user:
            # check password
            password = bcrypt.check_password_hash(
                user.password, login_form.password.data
            )
            # if password is true
            if password:
                # set the login and session
                login_user(
                    user,
                    remember=login_form.remember.data,
                    duration=datetime.timedelta(seconds=3600),
                )
                # determine the next page
                next_page = request.args.get("next")
                # make a flash message when login successfully
                flash(f"Welcome To Cicks Blog, {login_form.username.data}!😇", "success")
                # redirecting to main.home or next page
                return (
                    redirect(next_page) if next_page else redirect(url_for("main.home"))
                )
            # if password is false
            else:
                flash("Invalid password!😢", "error")
        # if user not found in database
        else:
            flash("Invalid username or password!😢", "error")
    # go back to login form
    return render_template("login.html", title="Login", form=login_form)


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("users.login"))


@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    update_form = UpdateForm()

    if update_form.validate_on_submit():
        # check if user update his picture profile
        if update_form.user_pict.data:
            pict_file = save_pict(update_form.user_pict.data)
            current_user.user_pict = pict_file
        # change with new username, email, and phone number
        current_user.username = update_form.username.data
        current_user.email = update_form.email.data
        current_user.phone_number = update_form.phone_number.data
        # commit data to database
        db.session.commit()
        # flash message when complete
        flash("Your account has been updated!😉", "success")
        # go back to account route
        return redirect(url_for("users.account"))
    # when form is not submitted
    elif request.method == "GET":
        # populating field with existing data
        update_form.username.data = current_user.username
        update_form.email.data = current_user.email
        update_form.phone_number.data = current_user.phone_number

    # set profile picture location
    img_profile = url_for("static", filename="img/" + current_user.user_pict)

    return render_template(
        "account.html", title="My Account", form=update_form, img=img_profile
    )


@users.route("/account/<string:username>", methods=["GET", "POST"])
def account_info(username):
    # determine user from username
    user = User.query.filter_by(username=username).first_or_404()
    # check if user is already login
    if current_user.is_authenticated:
        # jika parameter username sama dengan username yang sedang login,
        # maka beri akses untuk mengedit datanya
        if user.username == current_user.username:
            return redirect(url_for("users.account"))

    # set profile picture location
    img_profile = url_for("static", filename="img/" + user.user_pict)

    return render_template(
        "account_info.html", title="Account Info", user=user, img=img_profile
    )


@users.route("/user/<string:username>")
def user_posts(username):
    # determine the current page
    page = request.args.get("page", 1, type=int)
    # determine user from username
    user = User.query.filter_by(username=username).first_or_404()
    # query all data posts from user with pagination order by date posted
    posts = (
        Post.query.filter_by(author=user)
        .order_by(Post.date_posted.desc())
        .paginate(page=page, per_page=3)
    )

    return render_template(
        "user_posts.html",
        title=f"{user.username} Posts",
        user=user,
        posts=posts,
    )


@users.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    # check if user is already login
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    req_form = ResetRequestForm()

    if req_form.validate_on_submit():
        user = User.query.filter_by(email=req_form.email.data).first()
        send_token_email(user)
        flash(
            f'An email has been sent to  "{req_form.email.data}".\nCheck it to reset your password!🥰',
            "info",
        )
        return redirect(url_for("users.login"))

    return render_template("reset_request.html", title="Reset Password", form=req_form)


@users.route("/reset_password/<string:token>", methods=["GET", "POST"])
def reset_password(token):
    # check if user is already login
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    user = User.token_verification(token)

    if user is None:
        flash("The token you entered is incorrect or has expired!😌", "error")
        return redirect(url_for("users.reset_request"))

    reset_form = ResetPasswordForm()

    if reset_form.validate_on_submit():
        # hashed the password and reset new password from user
        user.password = bcrypt.generate_password_hash(reset_form.password.data).decode(
            "utf-8"
        )
        # insert user to database
        db.session.commit()
        # make a flash message when registration successfully
        flash("Your password has been reset, you can login now!😇", "success")
        # redirecting to login
        return redirect(url_for("users.login"))

    return render_template(
        "reset_password.html", title="Reset Password", form=reset_form
    )
