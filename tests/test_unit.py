"""Unit tests: site sources (config, sector data, logos, content), no Hugo build."""
import re
import struct
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

import pytest

from conftest import (CONTENT, ROOT, published_regular_pages, read_page,
                      section_dir, sectors, site_config)

SECTOR_DIRS = [s["path"] for s in sectors()]


# ---------------------------------------------------------------- config

def test_base_url_is_custom_domain():
    assert site_config()["baseURL"] == "https://yaserakhras.com/"


def test_cname_matches_base_url_host():
    cname = (ROOT / "static" / "CNAME").read_text(encoding="utf-8").strip()
    assert cname == urlparse(site_config()["baseURL"]).hostname


def test_theme_is_papermod_and_checked_out():
    assert site_config()["theme"] == "PaperMod"
    assert (ROOT / "themes" / "PaperMod" / "theme.toml").is_file(), \
        "PaperMod submodule missing: run `git submodule update --init`"


def test_home_lists_no_recent_items():
    assert site_config()["params"]["mainSections"] == []


def test_social_icons_github_then_email():
    icons = site_config()["params"]["socialIcons"]
    assert [i["name"] for i in icons] == ["github", "email"]
    assert icons[0]["url"] == "https://github.com/yakhras"
    assert re.fullmatch(r"mailto:[^@\s]+@[^@\s]+\.[a-z]+", icons[1]["url"])


def test_gitignore_excludes_build_and_local_files():
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").split()
    for entry in ("public/", "resources/_gen/", ".venv/", "*.stackdump"):
        assert entry in ignored


# ---------------------------------------------------------------- sectors data

def test_sector_names_and_order():
    assert [s["name"] for s in sectors()] == \
        ["ERP", "Linux / Red Hat", "Networking", "Programming"]


def test_programming_logo_order_is_c_cpp_python():
    programming = next(s for s in sectors() if s["name"] == "Programming")
    assert [i["file"] for i in programming["icons"]] == ["c.svg", "cplusplus.svg", "python.svg"]


@pytest.mark.parametrize("sector", sectors(), ids=lambda s: s["name"])
def test_sector_icons_are_valid(sector):
    assert sector["icons"], "sector without logo"
    for icon in sector["icons"]:
        assert re.fullmatch(r"#[0-9A-Fa-f]{6}", icon["color"]), icon
        assert isinstance(icon.get("wide", False), bool)
        svg = ROOT / "assets" / "sectors" / icon["file"]
        assert svg.is_file(), f"missing logo {svg}"
        root = ET.parse(svg).getroot()
        assert root.tag == "{http://www.w3.org/2000/svg}svg"
        assert root.get("viewBox") == "0 0 24 24"
        title = root.find("{http://www.w3.org/2000/svg}title")
        assert title is not None and title.text.strip(), "logo needs a <title> for accessibility"


@pytest.mark.parametrize("path", SECTOR_DIRS)
def test_sector_has_section_with_menu_entry(path):
    index = section_dir(path) / "_index.md"
    assert index.is_file(), f"{path} has no {index}"
    front, _ = read_page(index)
    assert front["title"]
    assert isinstance(front["menus"]["main"]["weight"], int)


def test_menu_order_follows_sector_order_and_about_is_last():
    weights = [read_page(section_dir(p) / "_index.md")[0]["menus"]["main"]["weight"]
               for p in SECTOR_DIRS]
    assert weights == sorted(weights) and len(set(weights)) == len(weights)
    about, _ = read_page(CONTENT / "about.md")
    assert about["menus"]["main"]["weight"] > max(weights)


@pytest.mark.parametrize("path", SECTOR_DIRS)
def test_sector_hidden_exactly_when_empty(path):
    """Empty sectors stay draft (no empty page live); sectors with content are published."""
    front, _ = read_page(section_dir(path) / "_index.md")
    has_content = bool(published_regular_pages(section_dir(path)))
    assert front.get("draft", False) is (not has_content), \
        f"{path}: draft={front.get('draft', False)} but has_content={has_content}"


def test_programming_subsections_order_c_cpp_before_python():
    c_cpp, _ = read_page(CONTENT / "programming" / "c-cpp" / "_index.md")
    python, _ = read_page(CONTENT / "programming" / "python" / "_index.md")
    assert c_cpp["weight"] < python["weight"]


# ---------------------------------------------------------------- content

def test_old_urls_have_redirect_aliases():
    erp, _ = read_page(CONTENT / "erp" / "_index.md")
    assert "/odoo/" in erp["aliases"]
    spt, _ = read_page(CONTENT / "erp" / "spt" / "index.md")
    assert {"/projects/spt/", "/odoo/spt/"} <= set(spt["aliases"])


def test_about_text():
    _, body = read_page(CONTENT / "about.md")
    text = " ".join(body.split())
    assert "{{< photo >}}" in text
    assert ("Passionate about infrastructure: ERP development, Linux / Red Hat systems, "
            "networking and programming in C, C++ and Python.") in text
    assert "This site collects" not in text
    assert "IT professional" not in text


@pytest.mark.parametrize("bundle", sorted(p.parent for p in CONTENT.rglob("index.md")),
                         ids=lambda p: p.relative_to(CONTENT).as_posix())
def test_page_bundle_images_exist(bundle):
    front, body = read_page(bundle / "index.md")
    refs = re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", body)
    cover = (front.get("cover") or {}).get("image")
    for ref in refs + ([cover] if cover else []):
        if not ref.startswith(("http://", "https://", "/")):
            assert (bundle / ref).is_file(), f"{bundle.name}: missing image {ref}"


def test_no_leftover_todo_or_draft_notes_in_published_pages():
    for md in CONTENT.rglob("*.md"):
        front, body = read_page(md)
        if front.get("draft", False):
            continue
        assert not re.search(r"\bTODO\b|<!--\s*DRAFT", body), f"{md} has a leftover note"


# ---------------------------------------------------------------- photo

def jpeg_size(path):
    data = path.read_bytes()
    assert data[:2] == b"\xff\xd8", "not a JPEG"
    i = 2
    while i < len(data):
        marker, length = data[i + 1], struct.unpack(">H", data[i + 2:i + 4])[0]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            return width, height
        i += 2 + length
    raise AssertionError("no JPEG frame header")


@pytest.mark.parametrize("name, size", [
    ("favicon-16x16.png", 16), ("favicon-32x32.png", 32), ("apple-touch-icon.png", 180)])
def test_favicons_have_expected_size(name, size):
    """PaperMod links these by default; generated by scripts/make_favicons.py."""
    data = (ROOT / "static" / name).read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", data[16:24]) == (size, size)


def test_favicon_ico_and_safari_mask_exist():
    assert (ROOT / "static" / "favicon.ico").read_bytes()[:4] == b"\x00\x00\x01\x00"
    ET.parse(ROOT / "static" / "safari-pinned-tab.svg")


def test_profile_photo_is_square_and_sharp_enough():
    width, height = jpeg_size(ROOT / "assets" / "images" / "photo.jpg")
    assert width == height, "photo must be square (shown as a circle)"
    assert width >= 360, "photo must be at least 2x the largest display size (180px)"
