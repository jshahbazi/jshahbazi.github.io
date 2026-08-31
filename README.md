# John Shahbazian's blog

A Markdown blog hosted by GitHub Pages at [jshahbazi.github.io](https://jshahbazi.github.io). Based on [Jekyll Now](https://github.com/barryclark/jekyll-now), with its MIT license retained.

## Hosting

GitHub Pages is already configured to build from `master`, at the repository root. Pushing or merging into `master` publishes automatically. Other branches do not publish. The build-check workflow validates changes without deploying them.

This is a static site: no database, server maintenance, or paid hosting is required for this public repository. Comments, authentication, and a browser-based CMS are not included.

## Write a post

1. Create `_posts/YYYY-MM-DD-short-title.md`. Use the intended publication date.
2. Add YAML front matter, followed by Markdown:

   ```markdown
   ---
   layout: post
   title: "Your post title"
   description: "A short summary for search results and link previews."
   ---

   An opening paragraph that introduces the topic.

   <!--more-->

   ## First section

   The rest of the post.
   ```

3. Preview and check the site.
4. Commit and push the post to a working branch. Merge into `master` when ready to publish.

The text before `<!--more-->` becomes the homepage excerpt. Posts appear newest first. Future-dated posts are omitted by default; GitHub does not rebuild simply because their publication date arrives. Push a change or trigger a Pages rebuild when that date arrives.

Keep a post's filename stable after publication because the title portion determines its URL. If it must change, set an explicit `permalink` in its front matter to preserve the old address.

## Drafts

Copy `_drafts/post-template.md` to another filename under `_drafts/`. Preview drafts with:

```sh
bundle exec jekyll serve --drafts
```

To publish, move the finished file into `_posts/` and add the date prefix. Normal builds exclude drafts.

**Drafts committed to this public repository are public source code**, even though they are absent from the website. Keep sensitive or private writing outside the repository.

## Preview locally with Ruby

Use Ruby 3.3 and Bundler; avoid macOS's bundled Ruby 2.6.

```sh
bundle install
bundle exec jekyll serve --host 127.0.0.1
```

Open [localhost:4000](http://localhost:4000). Restart Jekyll after changing `_config.yml`. Dependencies are pinned by `Gemfile.lock`; the `github-pages` gem matches the supported Pages dependency set.

## Preview with Docker

If you do not have a suitable Ruby installation, run these from the repository root:

```sh
docker run --rm -v "$PWD:/site" -v jshahbazi-blog-gems:/usr/local/bundle -w /site ruby:3.3 bundle install
docker run --rm -p 127.0.0.1:4000:4000 -v "$PWD:/site" -v jshahbazi-blog-gems:/usr/local/bundle -w /site ruby:3.3 bundle exec jekyll serve --host 0.0.0.0
```

The port is exposed only on your machine's loopback interface.

## Check before publishing

```sh
JEKYLL_ENV=production bundle exec jekyll build --strict_front_matter
python3 scripts/check_site.py
```

The same checks run in GitHub Actions on pushes and pull requests. They verify rendered routes, local links, RSS, HTTPS canonical URLs, and exclusion of draft and development files.

## Site settings

- `_config.yml`: name, description, site URL, timezone, and build configuration.
- `about.md`: biography and public profile links.
- `style.scss`: styling.
- `_layouts/`: shared page and post templates.
- `images/`: images referenced from posts.
- `feed.xml`: RSS feed; `sitemap.xml` is generated automatically.

The existing 2014 article and its `/Hello-World` URL are preserved. The site has no analytics or third-party comment scripts enabled.

The site URL uses HTTPS. GitHub's **Enforce HTTPS** setting is separate; it was disabled when this repository was inspected. It can be enabled under **Settings → Pages** when publishing the refresh.

## References

- [GitHub Pages publishing sources](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [Adding pages and posts](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll/adding-content-to-your-github-pages-site-using-jekyll)
