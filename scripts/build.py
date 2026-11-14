"""Build README tables from credits.yaml. Text outside the markers stays as written.

    python scripts/build.py          # rewrite README.md
    python scripts/build.py --check  # exit 1 if README.md is out of date (CI)
"""
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SECTIONS = {
    "models": ["Program", "Bootstrapped gets", "Expires", "Claude", "GPT", "Open models", "We got", "Checked"],
    "servers": ["Program", "Bootstrapped gets", "Expires", "We got", "Notes", "Checked"],
    "growth": ["Program", "What you get", "Expires", "Catch", "Checked"],
    "free": ["Service", "Free allowance", "Notes"],
}


def cells(r, cat):
    name = f"[{r['name']}]({r['url']})"
    got = r.get("we_got") or "-"
    if cat == "models":
        return [name, r["amount"], r["expires"], r["claude"], r["gpt"], r["open_models"], got, str(r["checked"])]
    if cat == "servers":
        return [name, r["amount"], r["expires"], got, r["notes"], str(r["checked"])]
    if cat == "growth":
        return [name, r["amount"], r["expires"], r["notes"], str(r["checked"])]
    return [name, r["amount"], r["notes"]]


def table(rows, cat):
    head = SECTIONS[cat]
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows:
        if r["category"] == cat and r["no_round"] != "no":
            out.append("| " + " | ".join(str(c).replace("|", "/") for c in cells(r, cat)) + " |")
    return "\n".join(out)


def render(text, rows):
    for cat in SECTIONS:
        start, end = f"<!-- {cat}:start -->", f"<!-- {cat}:end -->"
        a, b = text.index(start) + len(start), text.index(end)
        text = text[:a] + "\n" + table(rows, cat) + "\n" + text[b:]
    return text


def main():
    rows = yaml.safe_load((ROOT / "credits.yaml").read_text())
    readme = ROOT / "README.md"
    old = readme.read_text()
    new = render(old, rows)
    if "--check" in sys.argv:
        if new != old:
            sys.exit("README.md is out of date: run python scripts/build.py")
        return
    readme.write_text(new)
    print(f"{len(rows)} entries")


if __name__ == "__main__":
    main()
