# Build and preview

No local Ruby/bundler is assumed. Build via Docker (matches CI, Ruby 3.3):

```sh
docker run --rm -v "$PWD":/srv/jekyll -w /srv/jekyll -e JEKYLL_ENV=production ruby:3.3 \
  bash -lc 'bundle config set --local path vendor/bundle >/dev/null && bundle install --quiet && bundle exec jekyll build --strict_front_matter'
```

Add `--drafts` to the `jekyll build` command to include `_drafts/`. Note that this also publishes `_drafts/post-template.md`, so `check_site.py` will fail on a drafts build; rebuild without `--drafts` before validating.

- Validate: `python3 scripts/check_site.py` (checks `_site` pages, links, feed, sitemap).
- Preview: `python3 -m http.server 4321 --directory _site`. Post URLs are extensionless in production; locally use `/<slug>.html`.
- `vendor/` is gitignored and excluded in `_config.yml`. `docs/`, `scripts/`, and `AGENTS.md` are also excluded from the build.

## Theme notes

Neobrutalism "Blue" palette: `hsl(214,95%,93%)` background, `hsl(217,100%,66%)` main, 2px black borders, `--shadow: 4px 4px 0 0`, `--radius: 5px`, JetBrains Mono, light default with dark toggle. Primitives `.panel` / `.btn` / `.tag` / `.badge` live in `style.scss`. Posts use `category:` and `tags:` front matter to render chips.
