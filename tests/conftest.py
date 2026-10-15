"""Shared helpers and fixtures for the site tests.

Unit tests read the sources (config, data, content, assets) directly.
Integration tests build the site with Hugo the same way the deploy workflow does
(production environment, minified) and inspect the generated HTML.
"""
import os
import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path

import pytest
import tomli
import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
HUGO = os.environ.get("HUGO", "hugo")


# ---------------------------------------------------------------- sources

def load_toml(path):
    with open(path, "rb") as f:
        return tomli.load(f)


def site_config():
    return load_toml(ROOT / "config" / "_default" / "hugo.toml")


def sectors():
    return load_toml(ROOT / "data" / "sectors.toml")["sector"]


def read_page(path):
    """Return (front_matter: dict, body: str) of a YAML front-matter markdown file."""
    text = Path(path).read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.S)
    assert match, f"{path} has no YAML front matter"
    return yaml.safe_load(match.group(1)) or {}, match.group(2)


def section_dir(path):
    """'/erp' -> content/erp"""
    return CONTENT / path.strip("/")


def published_regular_pages(directory):
    """Non-draft regular pages (bundles' index.md or plain .md) under a directory."""
    pages = []
    for md in Path(directory).rglob("*.md"):
        if md.name == "_index.md":
            continue
        front, _ = read_page(md)
        if not front.get("draft", False):
            pages.append(md)
    return pages


# ---------------------------------------------------------------- build

def hugo_build(destination, drafts=False, environment="production"):
    args = [HUGO, "--source", str(ROOT), "--destination", str(destination),
            "--environment", environment, "--minify", "--cleanDestinationDir"]
    if drafts:
        args.append("--buildDrafts")
    result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
    return result


@pytest.fixture(scope="session")
def built_site(tmp_path_factory):
    """Production build: what goes live."""
    if shutil.which(HUGO) is None:
        pytest.skip("hugo not found on PATH")
    out = tmp_path_factory.mktemp("public")
    result = hugo_build(out)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ERROR" not in result.stdout + result.stderr
    return out


@pytest.fixture(scope="session")
def built_site_drafts(tmp_path_factory):
    """Build including draft (hidden) sectors, as when they get published."""
    if shutil.which(HUGO) is None:
        pytest.skip("hugo not found on PATH")
    out = tmp_path_factory.mktemp("public_drafts")
    result = hugo_build(out, drafts=True)
    assert result.returncode == 0, result.stdout + result.stderr
    return out


def page_file(public, url_path):
    """Map a site URL path ('/erp/spt/') to its file in the build output, or None."""
    rel = url_path.split("#")[0].split("?")[0].lstrip("/")
    candidate = public / rel
    if candidate.is_file():
        return candidate
    if (candidate / "index.html").is_file():
        return candidate / "index.html"
    return None


# ---------------------------------------------------------------- HTML

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "source", "track", "wbr", "path", "rect", "circle", "line", "polyline", "polygon"}


class Node:
    def __init__(self, tag, attrs, parent=None):
        self.tag = tag
        self.attrs = {k: (v if v is not None else "") for k, v in attrs}
        self.parent = parent
        self.children = []
        self._text = []

    @property
    def classes(self):
        return self.attrs.get("class", "").split()

    def text(self):
        parts = list(self._text)
        for child in self.children:
            parts.append(child.text())
        return " ".join(" ".join(parts).split())

    def iter(self):
        yield self
        for child in self.children:
            yield from child.iter()

    def find_all(self, tag=None, cls=None, id=None):
        return [n for n in self.iter() if n is not self
                and (tag is None or n.tag == tag)
                and (cls is None or cls in n.classes)
                and (id is None or n.attrs.get("id") == id)]

    def find(self, tag=None, cls=None, id=None):
        found = self.find_all(tag, cls, id)
        return found[0] if found else None


class _TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", [])
        self.current = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        self.current.children.append(Node(tag, attrs, self.current))

    def handle_endtag(self, tag):
        node = self.current
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.current = node.parent

    def handle_data(self, data):
        if data.strip():
            self.current._text.append(data.strip())


def parse_html(path):
    builder = _TreeBuilder()
    builder.feed(Path(path).read_text(encoding="utf-8"))
    return builder.root
