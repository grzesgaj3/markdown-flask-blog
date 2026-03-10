"""R Markdown (.Rmd) file parser."""

import re
import textwrap

import bleach
import frontmatter
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension


# Markdown extensions used for rendering
_MD_EXTENSIONS = [
    FencedCodeExtension(),
    CodeHiliteExtension(guess_lang=False, css_class="highlight"),
    TableExtension(),
    TocExtension(permalink=True),
    "markdown.extensions.extra",
    "markdown.extensions.smarty",
]

# Allowed HTML tags / attributes passed through bleach after Markdown render
_ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    "p", "pre", "code", "h1", "h2", "h3", "h4", "h5", "h6",
    "blockquote", "ul", "ol", "li", "strong", "em", "a", "img",
    "table", "thead", "tbody", "tr", "th", "td",
    "hr", "br", "div", "span", "sup", "sub",
]
_ALLOWED_ATTRIBUTES = {
    **bleach.sanitizer.ALLOWED_ATTRIBUTES,
    "*": ["class", "id"],
    "a": ["href", "title", "rel"],
    "img": ["src", "alt", "title"],
    "code": ["class"],
    "div": ["class"],
    "span": ["class"],
    "td": ["align"],
    "th": ["align"],
}


def _convert_r_chunks_to_fenced(text: str) -> str:
    """Replace R Markdown code chunks with fenced Markdown code blocks.

    Supports both regular R chunks (```{r ...}...```) and inline code.
    """
    # Named/option chunk: ```{r [label, options]}
    text = re.sub(
        r"```\{r([^}]*)\}",
        lambda m: "```r\n# chunk options:" + m.group(1).strip() if m.group(1).strip() else "```r",
        text,
    )
    # Generic language chunks: ```{python}, ```{bash}, etc.
    text = re.sub(
        r"```\{(\w+)([^}]*)\}",
        lambda m: f"```{m.group(1)}",
        text,
    )
    return text


def _strip_r_output_blocks(text: str) -> str:
    """Remove knitr output markers that may appear in pre-rendered .Rmd files."""
    text = re.sub(r"^##\s.*$", "", text, flags=re.MULTILINE)
    return text


def parse_rmd(filepath: str) -> dict:
    """Parse an R Markdown file and return a dict with metadata and HTML content.

    Returns a dict with keys:
        - title (str)
        - date (str)
        - author (str)
        - description (str)
        - tags (list[str])
        - slug (str)   – derived from filename without extension
        - content_html (str)  – sanitised HTML
    """
    post = frontmatter.load(filepath)

    slug = _slug_from_path(filepath)

    # Extract and normalise metadata
    meta = {
        "title": str(post.get("title", slug.replace("-", " ").title())),
        "date": str(post.get("date", "")),
        "author": str(post.get("author", "")),
        "description": str(post.get("description", "")),
        "tags": _normalise_tags(post.get("tags", [])),
        "slug": slug,
    }

    body = post.content
    body = _convert_r_chunks_to_fenced(body)
    body = _strip_r_output_blocks(body)

    md = markdown.Markdown(extensions=_MD_EXTENSIONS)
    raw_html = md.convert(body)

    clean_html = bleach.clean(
        raw_html,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        strip=False,
    )

    meta["content_html"] = clean_html
    meta["toc_html"] = getattr(md, "toc", "")
    return meta


def _slug_from_path(filepath: str) -> str:
    import os
    basename = os.path.basename(filepath)
    # Remove .Rmd or .rmd extension
    slug, _ = os.path.splitext(basename)
    return slug


def _normalise_tags(tags) -> list:
    if isinstance(tags, list):
        return [str(t) for t in tags]
    if isinstance(tags, str):
        return [t.strip() for t in tags.split(",") if t.strip()]
    return []
