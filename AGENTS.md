# AGENTS.md

Personal blog (Jekyll, GitHub Pages) for jshahbazi.github.io. Posts live in `_posts/`, unpublished candidates in `_drafts/`.

Detailed guidance lives in `docs/`:

- [docs/writing-style.md](docs/writing-style.md) — voice, vocabulary, and structure for posts, plus the format for LinkedIn posts announcing them. Read this before drafting or editing any post.
- [docs/build.md](docs/build.md) — how to build, validate, and preview the site locally.

## Quick rules

- Post filenames: `YYYY-MM-DD-slug.md`. Front matter requires `layout: post`, `category`, `tags`, `description`, `title`. Use `<!--more-->` after the first paragraph or two as the excerpt separator.
- Post URLs are extensionless (`permalink: /:title`); do not rename a published post's slug without a redirect.
- New drafts go in `_drafts/` until the author moves them to `_posts/`.
- Do not edit anything under `_site/` or `vendor/`; both are build output.
- Do not change numbers, tables, or quoted data in a post when restyling it. Preserve all figures exactly.
- Write for an experienced software engineer who is not an ML or evals specialist. State results up front, use plain words over field jargon (see the Vocabulary table in the style guide), and keep titles and headings descriptive rather than catchy.
