import json
import re
from scholarly import scholarly

SCHOLAR_ID = "F-S76iUAAAAJ"
HTML_FILE = "publications.html"
TARGET_FILES_FOR_STATS = ["index.html", "publications.html"]


def clean_title(title):
    return re.sub(r"[^a-zA-Z0-9]", "", (title or "").lower())


def extract_publications_block(html):
    pattern = re.compile(r"(// PUBLICATIONS_DATA_START\s*\n\s*const publications = )(.*?)(;\s*\n\s*// PUBLICATIONS_DATA_END)", re.DOTALL)
    match = pattern.search(html)
    if not match:
        raise RuntimeError("Could not find publications data block in publications.html")
    return pattern, match


def main():
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    pattern, match = extract_publications_block(html)
    publications = json.loads(match.group(2))

    print(f"Fetching Google Scholar profile: {SCHOLAR_ID}")
    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author, sections=["publications", "indices", "counts"])

    live_by_title = {}
    for pub in author.get("publications", []):
        title = pub.get("bib", {}).get("title", "")
        if title:
            live_by_title[clean_title(title)] = pub

    existing = {clean_title(p.get("title", "")) for p in publications}

    # Update citations for existing records.
    for record in publications:
        key = clean_title(record.get("title", ""))
        if key in live_by_title:
            record["citations"] = int(live_by_title[key].get("num_citations", 0) or 0)

    # Add new Google Scholar records without duplicating titles.
    for key, pub in live_by_title.items():
        if key in existing:
            continue
        bib = pub.get("bib", {})
        title = bib.get("title", "")
        if not title:
            continue
        year_raw = bib.get("pub_year") or bib.get("year") or 0
        try:
            year = int(year_raw)
        except Exception:
            year = 0
        authors = [a.strip() for a in re.split(r"\s+and\s+|,\s*", bib.get("author", "")) if a.strip()]
        publications.append({
            "title": title,
            "authors": authors,
            "venue": bib.get("venue") or bib.get("journal") or bib.get("citation") or "Google Scholar record",
            "year": year,
            "status": f"Google Scholar record {year}" if year else "Google Scholar record",
            "rank": "",
            "impactfactor": "",
            "type": "Publication",
            "citations": int(pub.get("num_citations", 0) or 0)
        })
        existing.add(key)

    # Deduplicate again by title in case manual data was edited.
    deduped = []
    seen = set()
    for p in publications:
        key = clean_title(p.get("title", ""))
        if key and key not in seen:
            deduped.append(p)
            seen.add(key)
    publications = deduped

    new_json = json.dumps(publications, ensure_ascii=False, indent=2)
    html = html[:match.start(2)] + new_json + html[match.end(2):]
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    citations = int(author.get("citedby", 0) or 0)
    hindex = int(author.get("hindex", 0) or 0)
    i10index = int(author.get("i10index", 0) or 0)

    for path in TARGET_FILES_FOR_STATS:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            content = re.sub(r'(id="scholar-citations" data-target=")[^"]*(")', rf'\g<1>{citations}\g<2>', content)
            content = re.sub(r'(id="scholar-hindex" data-target=")[^"]*(")', rf'\g<1>{hindex}\g<2>', content)
            content = re.sub(r'(id="scholar-i10index" data-target=")[^"]*(")', rf'\g<1>{i10index}\g<2>', content)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except FileNotFoundError:
            continue

    print(f"Updated {len(publications)} unique publications. Stats: citations={citations}, h-index={hindex}, i10-index={i10index}")


if __name__ == "__main__":
    main()
