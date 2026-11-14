"""Check that every program link in credits.yaml still answers. Exit 1 on dead links.

    python scripts/check_links.py
"""
import pathlib
import sys
import urllib.request

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
UA = "Mozilla/5.0 (bootstrapped-credits link check)"


def alive(url):
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.status < 400, r.status
        except urllib.error.HTTPError as e:
            # many sites block bots with 403/429: not a dead page
            if e.code in (401, 403, 429):
                return True, e.code
            last = e.code
        except Exception as e:
            last = type(e).__name__
    return False, last


def main():
    rows = yaml.safe_load((ROOT / "credits.yaml").read_text())
    dead = []
    for r in rows:
        ok, code = alive(r["url"])
        print(f"{'ok  ' if ok else 'DEAD'} {code} {r['url']}")
        if not ok:
            dead.append(r["name"])
    if dead:
        sys.exit("Dead links: " + ", ".join(dead))


if __name__ == "__main__":
    main()
