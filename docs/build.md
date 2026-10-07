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

Minimal editorial style: white background, `#e5e5e5` hairline borders, `--radius: 2px`, black filled primary button, `#2563eb` blue links/icons, Inter for text and JetBrains Mono for uppercase labels/meta. Light is the default; the header toggle switches to dark. Home has a large hero (`.hero`) plus a bordered two-column post grid (`.post-cards`); the footer is four icon tiles (`.footer-tiles`). Primitives `.btn` / `.panel` / `.tag` / `.label` live in `style.scss`. Posts use `category:` and `tags:` front matter to render the mono meta line.
