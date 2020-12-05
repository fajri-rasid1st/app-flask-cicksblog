from cicksblog.models import Post
from flask import render_template, request, Blueprint

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/home")
def home():
    # determine the current page
    page = request.args.get("page", 1, type=int)
    # query all data posts with pagination order by date posted
    posts = Post.query.order_by(Post.id.desc()).paginate(page=page, per_page=5)

    return render_template("home.html", title="Home", posts=posts)


@main.route("/about")
def about():
    return render_template("about.html", title="About")