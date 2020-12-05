from cicksblog import db
from cicksblog.models import Post
from cicksblog.posts.forms import PostForm
from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import current_user, login_required

# from flask import abort

posts = Blueprint("posts", __name__)


@posts.route("/post/new", methods=["GET", "POST"])
@login_required
def create_post():
    post_form = PostForm()

    if post_form.validate_on_submit():
        # instance PostModel
        post = Post(
            title=post_form.title.data,
            content=post_form.content.data,
            author=current_user,
        )
        # insert post to database
        db.session.add(post)
        db.session.commit()
        # make a flash message when create post successfully
        flash("Your post has been created!🙂", "success")
        # go back to main page
        return redirect(url_for("main.home"))

    return render_template(
        "post.html", title="Create Post", legend="Create New Post", form=post_form
    )


@posts.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    # get the current post
    post = Post.query.get_or_404(post_id)
    # check post author
    if post.author.id != current_user.id:
        # return abort(403)
        flash("You are not allowed to edit this post!🤔", "warning")
        return redirect(url_for("posts.current_post", post_id=post.id))
    # instance PostForm
    post_form = PostForm()
    # when form is submitted
    if post_form.validate_on_submit():
        # change with new title and content
        post.title = post_form.title.data
        post.content = post_form.content.data
        # commit data to database
        db.session.commit()
        # flash message when update complete
        flash("Your post has been updated!😉", "success")
        # go back to current post
        return redirect(url_for("posts.current_post", post_id=post.id))
    elif request.method == "GET":
        # populating field with existing data
        post_form.title.data = post.title
        post_form.content.data = post.content

    return render_template(
        "post.html", title="Edit Post", legend="Edit This Post", form=post_form
    )


@posts.route("/post/<int:post_id>/delete", methods=["GET", "POST"])
@login_required
def delete_post(post_id):
    # get the current post
    post = Post.query.get_or_404(post_id)
    # check post author
    if post.author.id != current_user.id:
        # return abort(403)
        flash("You are not allowed to delete this post!🤔", "warning")
        return redirect(url_for("posts.current_post", post_id=post.id))
    # delete post from database
    db.session.delete(post)
    db.session.commit()
    # flash message when delete complete
    flash("Your post has been deleted!😮", "success")

    return redirect(url_for("main.home"))


@posts.route("/post/<int:post_id>")
def current_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("current_post.html", title="Current Post", post=post)