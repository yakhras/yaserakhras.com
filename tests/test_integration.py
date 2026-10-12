"""Integration tests: build the site with Hugo (as the deploy does) and check the output."""
import base64
import hashlib
import re

import pytest

from conftest import page_file, parse_html, sectors

SITE = "https://yaserakhras.com"


def home(public):
    return parse_html(public / "index.html")


def menu_items(doc):
    menu = doc.find("ul", id="menu")
    return [(a.text(), a.attrs["href"]) for a in menu.find_all("a")]


def cards(doc):
    return doc.find("div", cls="sector-grid").find_all(cls="sector-card")


def local_path(url):
    """Site-local path of a URL, or None for external / non-http links."""
    if url.startswith(SITE):
        url = url[len(SITE):] or "/"
    if url.startswith("/") and not url.startswith("//"):
        return url
    return None


# ---------------------------------------------------------------- home

def test_menu_shows_published_sectors_and_about(built_site):
    assert menu_items(home(built_site)) == [("ERP", f"{SITE}/erp/"), ("About", f"{SITE}/about/")]


def test_home_cards_order_and_state(built_site):
    found = [(c.find(cls="sector-name").text(), c.tag, c.attrs.get("href"),
              "sector-soon" in c.classes) for c in cards(home(built_site))]
    assert found == [
        ("ERP", "a", "/erp/", False),
        ("Linux / Red Hat", "div", None, True),
        ("Networking", "div", None, True),
        ("Programming", "div", None, True),
    ]
    for card in cards(home(built_site))[1:]:
        assert card.find(cls="sector-badge").text() == "coming soon"


def test_home_card_logos(built_site):
    logos = [[t.text() for t in c.find_all("title")] for c in cards(home(built_site))]
    assert logos == [["Odoo"], ["Linux", "Red Hat"], ["Networking"], ["C", "C++", "Python"]]


def test_home_logo_hover_colours_match_data(built_site):
    for card, sector in zip(cards(home(built_site)), sectors()):
        styles = [s.attrs["style"].replace(" ", "").lower() for s in card.find_all(cls="sector-logo")]
        assert styles == [f"--brand:{i['color']}".lower() for i in sector["icons"]]


def test_home_has_no_recent_items_and_no_spt(built_site):
    doc = home(built_site)
    assert doc.find_all("article", cls="post-entry") == []
    assert "SPT" not in doc.find("main").text()


def test_home_name_heading_hidden_but_present(built_site):
    h1s = home(built_site).find_all("h1")
    assert len(h1s) == 1
    assert "visually-hidden" in h1s[0].classes and h1s[0].text() == "Yaser Akhras"


def test_home_photo_and_social_icons(built_site):
    doc = home(built_site)
    photo = doc.find("img", cls="profile-photo-home")
    assert photo is not None and photo.attrs["alt"] == "Yaser Akhras"
    for candidate in photo.attrs["srcset"].split(","):
        url = candidate.split()[0]
        assert page_file(built_site, local_path(url)) is not None, url
    links = [a.attrs["href"] for a in doc.find("div", cls="social-icons").find_all("a")]
    assert links[0] == "https://github.com/yakhras"
    assert links[1].startswith("mailto:")


# ---------------------------------------------------------------- pages

def test_about_page(built_site):
    doc = parse_html(page_file(built_site, "/about/"))
    content = doc.find("div", cls="post-content")
    assert content.find("img", cls="profile-photo-about") is not None
    assert content.text() == ("Passionate about infrastructure: ERP development, Linux / Red Hat "
                              "systems, networking and programming in C, C++ and Python.")


def test_erp_section_lists_spt(built_site):
    doc = parse_html(page_file(built_site, "/erp/"))
    links = [a.attrs.get("href") for a in doc.find("main").find_all("a")]
    assert f"{SITE}/erp/spt/" in links


def test_spt_page_links_repo_and_shows_screenshots(built_site):
    doc = parse_html(page_file(built_site, "/erp/spt/"))
    content = doc.find("div", cls="post-content")
    assert "https://github.com/yakhras/Odoo-SPT" in [a.attrs.get("href") for a in content.find_all("a")]
    images = content.find_all("img")
    assert len(images) >= 4
    for img in images:
        assert page_file(built_site, local_path(img.attrs["src"]) or img.attrs["src"]) is not None


@pytest.mark.parametrize("old, new", [
    ("/odoo/", "/erp/"),
    ("/odoo/spt/", "/erp/spt/"),
    ("/projects/spt/", "/erp/spt/"),
])
def test_old_urls_redirect(built_site, old, new):
    doc = parse_html(page_file(built_site, old))
    refresh = next(m for m in doc.find_all("meta") if m.attrs.get("http-equiv") == "refresh")
    assert refresh.attrs["content"].endswith(f"url={SITE}{new}")
    assert page_file(built_site, new) is not None


@pytest.mark.parametrize("hidden", ["/linux/", "/networking/", "/programming/",
                                    "/programming/python/", "/programming/c-cpp/"])
def test_hidden_sectors_not_published(built_site, hidden):
    assert page_file(built_site, hidden) is None
    assert hidden not in (built_site / "sitemap.xml").read_text(encoding="utf-8")


# ---------------------------------------------------------------- whole site

def test_cname_robots_and_sitemap(built_site):
    assert (built_site / "CNAME").read_text(encoding="utf-8").strip() == "yaserakhras.com"
    assert (built_site / "robots.txt").is_file()
    sitemap = (built_site / "sitemap.xml").read_text(encoding="utf-8")
    for url in ("/erp/", "/erp/spt/", "/about/"):
        assert f"{SITE}{url}" in sitemap


def test_stylesheet_integrity_and_custom_rules(built_site):
    link = next(l for l in home(built_site).find_all("link") if "stylesheet" in l.attrs.get("rel", ""))
    css_file = page_file(built_site, local_path(link.attrs["href"]))
    assert css_file is not None
    css = css_file.read_bytes()
    algo, expected = link.attrs["integrity"].split("-", 1)
    assert algo == "sha256"
    assert base64.b64encode(hashlib.sha256(css).digest()).decode() == expected, \
        "SRI hash mismatch: browsers would refuse the stylesheet"
    for selector in (b".sector-grid", b".profile-photo", b".visually-hidden"):
        assert selector in css


def test_all_internal_links_and_assets_resolve(built_site):
    broken = []
    for html in built_site.rglob("*.html"):
        doc = parse_html(html)
        for node in doc.iter():
            for attr in ("href", "src"):
                path = local_path(node.attrs.get(attr, "")) if hasattr(node, "attrs") else None
                if path and page_file(built_site, path) is None:
                    broken.append(f"{html.relative_to(built_site)}: {attr}={path}")
    assert broken == []


# ---------------------------------------------------------------- hidden sectors once published

def test_draft_build_publishes_all_sectors_in_order(built_site_drafts):
    doc = home(built_site_drafts)
    assert [name for name, _ in menu_items(doc)] == \
        ["ERP", "Linux", "Networking", "Programming", "About"]
    assert [c.attrs.get("href") for c in cards(doc)] == \
        ["/erp/", "/linux/", "/networking/", "/programming/"]
    assert all(c.tag == "a" and "sector-soon" not in c.classes for c in cards(doc))
