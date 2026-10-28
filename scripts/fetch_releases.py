"""Download the module zips the ERP pages offer, so the site serves them itself.

For every page bundle with `releases` in its front matter (content/erp/<slug>/index.md):

    module: goatcounter_stats
    repo: yakhras/Odoo-GoatCounter-Stats
    releases: {"20.0": "20.0.1.2.2", "19.0": "19.0.1.2.3"}

it downloads <module>-<version>.zip from the GitHub release <version> into the bundle (Hugo
publishes it next to the page), checks it against the release's .sha256 file, and writes
data/releases.json with the size, SHA-256 and release date that the {{< versions >}} cards show.
A zip already present with the right checksum isn't downloaded again.

The zips and data/releases.json are build output (git-ignored). The deploy workflow and the
test fixture run this before Hugo. Run it by hand before `hugo server`:
    python scripts/fetch_releases.py
Set GITHUB_TOKEN to avoid the API's 60 requests/hour limit for anonymous calls.
"""
import hashlib
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
DATA = ROOT / "data" / "releases.json"


def get(url, accept=None):
    req = urllib.request.Request(url, headers={"User-Agent": "yaserakhras.com-build"})
    if accept:
        req.add_header("Accept", accept)
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def front_matter(md):
    text = md.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
    return yaml.safe_load(match.group(1)) or {} if match else {}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    data, problems = {}, []
    for md in sorted(CONTENT.rglob("index.md")):
        front = front_matter(md)
        if not front.get("releases"):
            continue
        slug, module, repo = md.parent.name, front["module"], front["repo"]
        if sorted(front["releases"]) != sorted(front.get("odoo", [])):
            problems.append(f"{slug}: `releases` series {sorted(front['releases'])} "
                            f"differ from `odoo` {sorted(front.get('odoo', []))}")
        for series, version in front["releases"].items():
            if not version.startswith(series + "."):
                problems.append(f"{slug}: release {version} is not a {series} version")
                continue
            name = f"{module}-{version}.zip"
            base = f"https://github.com/{repo}/releases/download/{version}"
            try:
                expected = get(f"{base}/{name}.sha256").decode().split()[0]
                target = md.parent / name
                if not target.exists() or sha256(target) != expected:
                    target.write_bytes(get(f"{base}/{name}"))
                    if sha256(target) != expected:
                        target.unlink()
                        raise ValueError("SHA-256 mismatch")
                release = json.loads(get(f"https://api.github.com/repos/{repo}/releases/tags/{version}",
                                         accept="application/vnd.github+json"))
            except Exception as e:  # noqa: BLE001 - report every missing release, then fail
                problems.append(f"{slug} {version}: {e}")
                continue
            data.setdefault(slug, {})[series] = {
                "version": version,
                "file": name,
                "size": target.stat().st_size,
                "sha256": expected,
                "date": release["published_at"][:10],
                "url": release["html_url"],
            }
            print(f"{slug} {version}: {name} ({target.stat().st_size} bytes)")
    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for p in problems:
        print("!!", p, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
