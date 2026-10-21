"""Integration tests: build the site with Hugo (as the deploy does) and check the output."""
import base64
import hashlib
import re
import shutil

import pytest

from conftest import (CONTENT, HUGO, hugo_build, page_file, parse_html, read_page,
                      sectors)

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


def project_pages():
    """URL paths of every published project page bundle (content/<sector>/.../<page>/index.md)."""
    pages = []
    for md in sorted(CONTENT.rglob("index.md")):
        if md.parent.parent == CONTENT or read_page(md)[0].get("draft", False):
            continue  # top-level pages (about) and drafts
        pages.append("/" + md.parent.relative_to(CONTENT).as_posix() + "/")
    return pages


def test_project_pages_found():
    assert "/erp/spt/" in project_pages()


@pytest.mark.parametrize("path", project_pages())
def test_project_page_is_listed_in_its_section(built_site, path):
    section = path.rstrip("/").rsplit("/", 1)[0] + "/"
    doc = parse_html(page_file(built_site, section))
    links = [a.attrs.get("href") for a in doc.find("main").find_all("a")]
    assert f"{SITE}{path}" in links


@pytest.mark.parametrize("path", project_pages())
def test_project_page_links_repo_license_and_shows_screenshots(built_site, path):
    doc = parse_html(page_file(built_site, path))
    content = doc.find("div", cls="post-content")
    hrefs = [a.attrs.get("href") or "" for a in content.find_all("a")]
    assert any(re.match(r"https://github\.com/yakhras/[\w.-]+$", h) for h in hrefs), "no repo link"
    # raw HTML: Node.text() doesn't keep inline elements in order
    raw = page_file(built_site, path).read_text(encoding="utf-8")
    assert re.search(r"License:</strong>\s*(LGPL-3|AGPL-3|GPL-3|MIT|Apache-2\.0)\b", raw), "no license"
    images = content.find_all("img")
    assert images, "no screenshots"
    for img in images:
        assert page_file(built_site, local_path(img.attrs["src"]) or img.attrs["src"]) is not None


@pytest.mark.parametrize("old, new", [
    ("/odoo/", "/erp/"),
    ("/odoo/spt/", "/erp/spt/"),
    ("/projects/spt/", "/erp/spt/"),
    ("/blog/", "/"),
    ("/project/", "/"),
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


# ---------------------------------------------------------------- odoo versions

def odoo_versions():
    """{version: [project URL paths]} from the ERP pages' front matter."""
    found = {}
    for path in project_pages():
        if not path.startswith("/erp/"):
            continue
        front, _ = read_page(CONTENT / path.strip("/") / "index.md")
        for version in front.get("odoo", []):
            found.setdefault(version, []).append(path)
    return found


def chips(doc):
    nav = doc.find("nav", cls="odoo-filter")
    return [(a.text(), a.attrs["href"], "active" in a.classes) for a in nav.find_all("a")]


def entry_links(doc):
    return sorted(local_path(a.attrs["href"]) for a in doc.find_all("a", cls="entry-link"))


def test_erp_shows_version_chips(built_site):
    versions = odoo_versions()
    total = len([p for p in project_pages() if p.startswith("/erp/")])
    expected = [(f"All ({total})", "/erp/", True)] + [
        (f"Odoo {v} ({len(versions[v])})", f"/erp/odoo/{v}/", False)
        for v in sorted(versions, key=lambda v: [int(x) for x in v.split(".")], reverse=True)]
    assert chips(parse_html(page_file(built_site, "/erp/"))) == expected


@pytest.mark.parametrize("version", sorted(odoo_versions()))
def test_version_page_lists_exactly_its_modules(built_site, version):
    doc = parse_html(page_file(built_site, f"/erp/odoo/{version}/"))
    assert doc.find("h1").text().startswith(f"Odoo {version} modules")
    assert entry_links(doc) == sorted(odoo_versions()[version])
    active = [c for c in chips(doc) if c[2]]
    assert [c[1] for c in active] == [f"/erp/odoo/{version}/"]
    crumbs = [(a.text(), a.attrs["href"]) for a in doc.find("nav", cls="breadcrumbs").find_all("a")]
    assert crumbs == [("Home", "/"), ("ERP", "/erp/")]


def test_bare_version_index_redirects_to_erp(built_site):
    html = page_file(built_site, "/erp/odoo/").read_text(encoding="utf-8").replace('"', "")
    assert "http-equiv=refresh" in html and f"url={SITE}/erp/" in html


def test_erp_cards_show_version_badges(built_site):
    doc = parse_html(page_file(built_site, "/erp/"))
    for entry in doc.find_all("article", cls="post-entry"):
        path = local_path(entry.find("a", cls="entry-link").attrs["href"])
        front, _ = read_page(CONTENT / path.strip("/") / "index.md")
        badges = [b.text() for b in entry.find_all("span", cls="odoo-badge")]
        assert badges == [f"Odoo {v}" for v in sorted(front["odoo"], reverse=True)], path


@pytest.mark.parametrize("path", [p for p in project_pages() if p.startswith("/erp/")])
def test_project_page_version_line_links_version_pages(built_site, path):
    content = parse_html(page_file(built_site, path)).find("div", cls="post-content")
    links = [(a.text(), a.attrs.get("href")) for a in content.find_all("a")]
    front, _ = read_page(CONTENT / path.strip("/") / "index.md")
    for version in front["odoo"]:
        assert (version, f"/erp/odoo/{version}/") in links



@pytest.mark.parametrize("path", [p for p in project_pages() if (CONTENT / p.strip("/") / "icon.png").exists()])
def test_section_card_shows_module_icon(built_site, path):
    section = path.rstrip("/").rsplit("/", 1)[0] + "/"
    doc = parse_html(page_file(built_site, section))
    card = next(a.parent for a in doc.find_all("a", cls="entry-link") if a.attrs.get("href") == f"{SITE}{path}")
    icon = card.find("img", cls="entry-icon")
    assert icon is not None and icon.attrs["src"].endswith(f"{path}icon.png")
    assert page_file(built_site, f"{path}icon.png") is not None

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


# ---------------------------------------------------------------- analytics

GOATCOUNTER = "https://yaserakhras.goatcounter.com/count"


def goatcounter_scripts(doc):
    return [s for s in doc.find_all("script") if "data-goatcounter" in s.attrs]


def test_every_page_loads_goatcounter_once(built_site):
    for html in built_site.rglob("*.html"):
        doc = parse_html(html)
        if any(m.attrs.get("http-equiv") == "refresh" for m in doc.find_all("meta")):
            continue  # alias redirect stubs (e.g. /erp/page/1/)
        scripts = goatcounter_scripts(doc)
        assert len(scripts) == 1, html.relative_to(built_site)
        assert scripts[0].attrs["data-goatcounter"] == GOATCOUNTER
        assert scripts[0].attrs["src"] == "https://gc.zgo.at/count.js"


def test_dev_build_has_no_goatcounter(tmp_path):
    if shutil.which(HUGO) is None:
        pytest.skip("hugo not found on PATH")
    result = hugo_build(tmp_path, environment="development")
    assert result.returncode == 0, result.stdout + result.stderr
    assert goatcounter_scripts(home(tmp_path)) == []


def test_old_url_redirect_is_counted(built_site):
    doc = parse_html(page_file(built_site, "/blog/"))
    scripts = goatcounter_scripts(doc)
    assert len(scripts) == 1 and scripts[0].attrs["data-goatcounter"] == GOATCOUNTER
    assert "redirect:" in scripts[0].attrs["onload"]


def test_home_clicks_are_tracked(built_site):
    doc = home(built_site)
    tracked = [c.attrs.get("data-goatcounter-click") for c in cards(doc) if c.tag == "a"]
    assert tracked == ["sector-erp"]
    icons = doc.find(cls="social-icons").find_all("a")
    assert [a.attrs.get("data-goatcounter-click") for a in icons] == ["social-github", "social-email"]


# ---------------------------------------------------------------- hidden sectors once published

def test_draft_build_publishes_all_sectors_in_order(built_site_drafts):
    doc = home(built_site_drafts)
    assert [name for name, _ in menu_items(doc)] == \
        ["ERP", "Linux", "Networking", "Programming", "About"]
    assert [c.attrs.get("href") for c in cards(doc)] == \
        ["/erp/", "/linux/", "/networking/", "/programming/"]
    assert all(c.tag == "a" and "sector-soon" not in c.classes for c in cards(doc))
