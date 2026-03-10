# 📝 R Markdown Flask Blog

A production-ready Flask blog that serves blog posts written in **R Markdown** (`.Rmd`) format.

![Blog homepage](https://github.com/user-attachments/assets/826595a8-0494-4ed8-b16a-a5665a79023c)

## Features

- 📄 Blog posts authored in **R Markdown** (`.Rmd`) with YAML front matter
- 🎨 **Syntax highlighting** for R code chunks and other languages (Pygments)
- 📑 Auto-generated **table of contents** per post
- 🏷️ Tag, date and author metadata
- 📖 Paginated post listing
- 🔒 Path-traversal protection for post slugs
- 🚀 Ready for production via **Gunicorn** WSGI

## Project Structure

```
markdown-flask-blog/
├── app/
│   ├── __init__.py        # Flask app factory
│   ├── routes.py          # URL routes
│   ├── rmd_parser.py      # R Markdown → HTML parser
│   └── templates/         # Jinja2 templates
│       ├── base.html
│       ├── index.html
│       ├── post.html
│       ├── about.html
│       ├── 404.html
│       └── 500.html
├── posts/                 # .Rmd blog post files
│   ├── hello-world.Rmd
│   ├── analiza-danych.Rmd
│   └── modele-liniowe.Rmd
├── static/
│   └── css/
│       ├── style.css
│       └── pygments.css
├── tests/
│   └── test_app.py
├── config.py              # Development / Production / Testing config
├── wsgi.py                # WSGI entry point
└── requirements.txt
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run in development mode

```bash
FLASK_ENV=development python wsgi.py
```

Visit <http://127.0.0.1:5000>.

### 3. Run in production with Gunicorn

```bash
gunicorn wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## Writing Blog Posts

Create a `.Rmd` file in the `posts/` directory with a YAML front matter header:

```
---
title: "My Post Title"
date: "2025-01-01"
author: "Your Name"
description: "A short description shown on the listing page."
tags: ["R", "statistics"]
---

## Introduction

Regular **Markdown** content goes here.
```

The post will appear automatically at `/post/<filename-without-extension>`.

## Environment Variables

| Variable         | Default                   | Description                            |
|------------------|---------------------------|----------------------------------------|
| `FLASK_ENV`      | `default`                 | `development`, `production`, `testing` |
| `SECRET_KEY`     | `change-me-in-production` | Flask secret key                       |
| `POSTS_DIR`      | `./posts`                 | Directory containing `.Rmd` files      |
| `POSTS_PER_PAGE` | `10`                      | Number of posts per page               |

## Running Tests

```bash
python -m pytest tests/ -v
```

## Tech Stack

- [Flask](https://flask.palletsprojects.com/) – web framework
- [Python-Markdown](https://python-markdown.github.io/) – Markdown rendering
- [Pygments](https://pygments.org/) – code syntax highlighting
- [python-frontmatter](https://github.com/eyeseast/python-frontmatter) – YAML front matter parsing
- [bleach](https://bleach.readthedocs.io/) – HTML sanitisation
- [Gunicorn](https://gunicorn.org/) – production WSGI server
- [Bootstrap 5](https://getbootstrap.com/) – responsive UI
