"""Check a production Jekyll build without third-party dependencies."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse
import xml.etree.ElementTree as ET

ROOT = Path("_site")
ORIGIN = "https://jshahbazi.github.io"


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.canonical = None
        self.description = None
        self.has_main = False
        self.h1_count = 0
        self.lang = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "main":
            self.has_main = True
        if tag == "h1":
            self.h1_count += 1
        if tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content")
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])
        if tag in ("img", "script") and "src" in attrs:
            self.links.append(attrs["src"])
        if tag == "link" and attrs.get("rel") in ("stylesheet", "icon"):
            self.links.append(attrs["href"])


def exists_at(url_path):
    path = ROOT / unquote(url_path).lstrip("/")
    return any(p.is_file() for p in (path, path / "index.html", Path(str(path) + ".html")))


for required in (
    "index.html",
    "about/index.html",
    "Hello-World.html",
    "404.html",
    "style.css",
    "favicon.svg",
    "feed.xml",
    "sitemap.xml",
):
    assert (ROOT / required).is_file(), f"Missing output: {required}"

for excluded in (
    "_drafts",
    "post-template.html",
    "README.md",
    "Gemfile",
    "Gemfile.lock",
    "scripts",
    "vendor",
    ".github",
    "AGENTS.md",
):
    assert not (ROOT / excluded).exists(), f"Development content published: {excluded}"

pages = list(ROOT.rglob("*.html"))
for file in pages:
    html = file.read_text()
    assert "{{" not in html and "{%" not in html, f"Unrendered Liquid: {file}"
    page = Page()
    page.feed(html)
    assert page.lang == "en", f"Missing or incorrect language: {file}"
    assert page.has_main, f"No main landmark: {file}"
    assert page.h1_count == 1, f"Expected one h1 in {file}, found {page.h1_count}"
    assert page.description and page.description.strip(), f"Missing meta description: {file}"
    assert page.canonical and page.canonical.startswith(ORIGIN + "/"), f"Incorrect canonical URL: {file}"
    for link in page.links:
        parsed = urlparse(link)
        if parsed.netloc and parsed.netloc != urlparse(ORIGIN).netloc:
            continue
        if parsed.scheme not in ("", "https", "http") or not parsed.path:
            continue
        if parsed.path.startswith("/"):
            assert exists_at(parsed.path), f"Broken local link in {file}: {link}"
        else:
            base = file.parent.relative_to(ROOT)
            assert exists_at(str(base / parsed.path)), f"Broken relative link in {file}: {link}"

feed = ET.parse(ROOT / "feed.xml")
items = feed.findall("./channel/item")
assert items, "RSS feed lost the existing article"
for item in items:
    link = item.findtext("link")
    assert link and link.startswith(ORIGIN + "/"), f"Incorrect RSS link: {link}"
    assert exists_at(urlparse(link).path), f"RSS item points to missing page: {link}"
ET.parse(ROOT / "sitemap.xml")
print(f"Checked {len(pages)} pages, metadata, internal links, {len(items)} RSS items, sitemap, and production exclusions.")
