"""URL routes for the Flask blog."""

import os

from flask import Blueprint, abort, current_app, render_template, request

from .rmd_parser import parse_rmd

bp = Blueprint("blog", __name__)


def _load_posts(posts_dir: str) -> list[dict]:
    """Load and sort all .Rmd posts from *posts_dir*, newest first."""
    posts = []
    if not os.path.isdir(posts_dir):
        return posts
    for filename in os.listdir(posts_dir):
        if filename.lower().endswith(".rmd"):
            filepath = os.path.join(posts_dir, filename)
            try:
                post = parse_rmd(filepath)
                posts.append(post)
            except Exception:
                current_app.logger.exception("Failed to parse %s", filename)
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


@bp.route("/")
def index():
    posts_dir = current_app.config["POSTS_DIR"]
    per_page = current_app.config["POSTS_PER_PAGE"]
    page = request.args.get("page", 1, type=int)
    if page < 1:
        abort(404)

    all_posts = _load_posts(posts_dir)
    total = len(all_posts)
    start = (page - 1) * per_page
    end = start + per_page
    posts = all_posts[start:end]

    has_prev = page > 1
    has_next = end < total

    return render_template(
        "index.html",
        posts=posts,
        page=page,
        has_prev=has_prev,
        has_next=has_next,
    )


@bp.route("/post/<slug>")
def post(slug: str):
    posts_dir = current_app.config["POSTS_DIR"]

    # Only allow safe slug characters to prevent path traversal
    if not slug.replace("-", "").replace("_", "").isalnum():
        abort(404)

    filepath = os.path.join(posts_dir, f"{slug}.Rmd")
    if not os.path.isfile(filepath):
        # try lowercase extension
        filepath = os.path.join(posts_dir, f"{slug}.rmd")
    if not os.path.isfile(filepath):
        abort(404)

    # Resolve the real path and ensure it stays within posts_dir
    real_filepath = os.path.realpath(filepath)
    real_posts_dir = os.path.realpath(posts_dir)
    if not real_filepath.startswith(real_posts_dir + os.sep):
        abort(404)

    post_data = parse_rmd(real_filepath)
    return render_template("post.html", post=post_data)


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@bp.errorhandler(500)
def internal_error(e):
    return render_template("500.html"), 500
