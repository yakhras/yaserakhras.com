# yaserakhras.com

Source of [yaserakhras.com](https://yaserakhras.com): Hugo + PaperMod, deployed to GitHub Pages
on every push to `main`.

## Site map

| Sector | Folder | Menu | Status |
|---|---|---|---|
| ERP (Odoo) | `content/erp/` | ERP | live |
| Linux / Red Hat | `content/linux/` | Linux | hidden (draft) |
| Networking | `content/networking/` | Networking | hidden (draft) |
| Programming | `content/programming/` (`c-cpp/`, `python/`) | Programming | hidden (draft) |
| About | `content/about.md` | About | live |

Each sector's `_index.md` holds its intro text and its menu entry. While it has `draft: true`,
the sector page and its menu item are left out of the site.

## Adding an item

1. Create a page bundle in the sector folder:
   ```
   hugo new content linux/my-item/index.md
   ```
2. Put images next to `index.md`, and name the cover image `feature.png`.
3. Add `tags` that cross sectors (e.g. `python` on a Linux automation script), so visitors can
   follow a topic across sectors via `/tags/`.
4. **First item in a hidden sector:** set `draft: false` in that sector's `_index.md` (and in
   `programming/c-cpp/_index.md` or `programming/python/_index.md` when applicable).
   The sector then appears in the menu.
5. Preview with `hugo server -D --renderToMemory`, run the tests, then push.

## Tests

`tests/test_unit.py` checks the sources (config, sector data, logos, content, photo, favicons).
`tests/test_integration.py` builds the site like the deploy does and checks the output (menu, home cards,
redirects, hidden sectors, stylesheet integrity, every internal link and image).

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-test.txt
.venv/Scripts/python -m pytest
```

The deploy workflow runs the same tests before building: a failing test blocks the deploy.
Some tests encode current decisions (sector names and order, the About text). Update them along with
the content when those change.

After replacing `assets/images/photo.jpg`, regenerate the tab icons with `scripts/make_favicons.py`
(needs `pip install Pillow`).
