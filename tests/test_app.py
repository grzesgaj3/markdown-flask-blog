"""Tests for the Flask R Markdown blog."""

import os
import textwrap
import pytest

# Make sure the project root is on sys.path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.rmd_parser import parse_rmd, _convert_r_chunks_to_fenced, _normalise_tags


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def tmp_posts(tmp_path):
    """Create a temporary posts directory with sample .Rmd files."""
    posts_dir = tmp_path / "posts"
    posts_dir.mkdir()

    (posts_dir / "hello-world.Rmd").write_text(
        textwrap.dedent("""\
            ---
            title: "Hello World"
            date: "2025-01-01"
            author: "Tester"
            description: "Test post."
            tags: ["test", "flask"]
            ---

            ## Introduction

            This is **bold** and *italic*.

            ```{r}
            summary(iris)
            ```
        """),
        encoding="utf-8",
    )

    (posts_dir / "second-post.Rmd").write_text(
        textwrap.dedent("""\
            ---
            title: "Second Post"
            date: "2025-02-01"
            author: "Author"
            ---

            Content here.
        """),
        encoding="utf-8",
    )

    return posts_dir


@pytest.fixture()
def app(tmp_posts):
    app = create_app("testing")
    app.config.update(
        TESTING=True,
        POSTS_DIR=str(tmp_posts),
    )
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


# ── rmd_parser tests ──────────────────────────────────────────────────────────

class TestConvertRChunks:
    def test_basic_r_chunk(self):
        text = "```{r}\ncode\n```"
        result = _convert_r_chunks_to_fenced(text)
        assert result.startswith("```r")

    def test_named_r_chunk(self):
        text = "```{r my_chunk, echo=FALSE}\ncode\n```"
        result = _convert_r_chunks_to_fenced(text)
        assert "```r" in result

    def test_python_chunk(self):
        text = "```{python}\nprint('hi')\n```"
        result = _convert_r_chunks_to_fenced(text)
        assert result.startswith("```python")

    def test_no_change_plain_fenced(self):
        text = "```r\ncode\n```"
        result = _convert_r_chunks_to_fenced(text)
        assert result == "```r\ncode\n```"


class TestNormaliseTags:
    def test_list_input(self):
        assert _normalise_tags(["a", "b"]) == ["a", "b"]

    def test_string_input(self):
        assert _normalise_tags("a, b, c") == ["a", "b", "c"]

    def test_empty(self):
        assert _normalise_tags([]) == []

    def test_none(self):
        assert _normalise_tags(None) == []


class TestParseRmd:
    def test_parses_metadata(self, tmp_posts):
        filepath = str(tmp_posts / "hello-world.Rmd")
        post = parse_rmd(filepath)
        assert post["title"] == "Hello World"
        assert post["date"] == "2025-01-01"
        assert post["author"] == "Tester"
        assert post["description"] == "Test post."
        assert "test" in post["tags"]
        assert post["slug"] == "hello-world"

    def test_content_is_html(self, tmp_posts):
        filepath = str(tmp_posts / "hello-world.Rmd")
        post = parse_rmd(filepath)
        assert "<strong>bold</strong>" in post["content_html"]
        assert "<em>italic</em>" in post["content_html"]

    def test_r_chunk_rendered_as_code(self, tmp_posts):
        filepath = str(tmp_posts / "hello-world.Rmd")
        post = parse_rmd(filepath)
        # R code should appear inside a highlighted code block;
        # Pygments wraps tokens in <span> elements so check for the raw text
        # after stripping HTML tags.
        import re
        plain = re.sub(r"<[^>]+>", "", post["content_html"])
        assert "summary(iris)" in plain

    def test_missing_optional_fields(self, tmp_posts):
        filepath = str(tmp_posts / "second-post.Rmd")
        post = parse_rmd(filepath)
        assert post["description"] == ""
        assert post["tags"] == []


# ── Route tests ───────────────────────────────────────────────────────────────

class TestIndexRoute:
    def test_status_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_shows_post_titles(self, client):
        resp = client.get("/")
        data = resp.data.decode("utf-8")
        assert "Hello World" in data
        assert "Second Post" in data

    def test_pagination_invalid_page(self, client):
        resp = client.get("/?page=0")
        assert resp.status_code == 404

    def test_pagination_page_2_empty(self, client):
        resp = client.get("/?page=2")
        assert resp.status_code == 200


class TestPostRoute:
    def test_existing_post(self, client):
        resp = client.get("/post/hello-world")
        assert resp.status_code == 200
        data = resp.data.decode("utf-8")
        assert "Hello World" in data

    def test_missing_post_returns_404(self, client):
        resp = client.get("/post/does-not-exist")
        assert resp.status_code == 404

    def test_path_traversal_rejected(self, client):
        resp = client.get("/post/../config")
        # Flask routing will either 404 or redirect – either way not 200 with config content
        assert resp.status_code in (301, 302, 404)

    def test_slug_with_special_chars_rejected(self, client):
        resp = client.get("/post/../../etc/passwd")
        assert resp.status_code in (301, 302, 404)


class TestAboutRoute:
    def test_status_200(self, client):
        resp = client.get("/about")
        assert resp.status_code == 200

    def test_contains_expected_content(self, client):
        resp = client.get("/about")
        data = resp.data.decode("utf-8")
        assert "Flask" in data


class TestErrorHandlers:
    def test_404_returns_html(self, client):
        resp = client.get("/nonexistent-route-xyz")
        assert resp.status_code == 404
        assert b"404" in resp.data
