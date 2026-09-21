# AGENTS.md

Personal blog (Jekyll, GitHub Pages) for jshahbazi.github.io. Posts live in `_posts/`, unpublished candidates in `_drafts/`.

Detailed guidance lives in `docs/`:

- [docs/writing-style.md](docs/writing-style.md) — voice and structure for posts. Read this before drafting or editing any post.
- [docs/build.md](docs/build.md) — how to build, validate, and preview the site locally.

## Quick rules

- Post filenames: `YYYY-MM-DD-slug.md`. Front matter requires `layout: post`, `category`, `tags`, `description`, `title`. Use `<!--more-->` after the first paragraph or two as the excerpt separator.
- Post URLs are extensionless (`permalink: /:title`); do not rename a published post's slug without a redirect.
- New drafts go in `_drafts/` until the author moves them to `_posts/`.
- Do not edit anything under `_site/` or `vendor/`; both are build output.
- Do not change numbers, tables, or quoted data in a post when restyling it. Preserve all figures exactly.
