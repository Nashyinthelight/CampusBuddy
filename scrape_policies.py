"""
scrape_policies.py — FAU Policy Scraper for PolicyOwl
Uses the internal AJAX API: B.GetContent.actor?BookId=XXXXX&PageId=-1
Much more reliable than HTML scraping since content loads via JS.
"""

import time
import re
import os
import json
import requests
from bs4 import BeautifulSoup

CONTENT_API = "https://faupub.cfmnetwork.com/B.GetContent.actor?BookId={book_id}&PageId={page_id}"

# Priority 1: IT/Security policies (10.x)
PRIORITY_1 = [
    (14282, "10.1_university_administrative_data_systems"),
    (14283, "10.2_acceptable_use_of_technology"),
    (14284, "10.3_responsible_use_of_data_access"),
    (14285, "10.4_digital_millennium_copyright_act"),
    (14286, "10.5_privacy_of_electronic_communications"),
    (14287, "10.6_security_awareness_training"),
    (14288, "10.7_system_and_data_classifications"),
    (14382, "10.8_payment_card_security"),
    (14383, "10.9_cloud_service_providers"),
    (14384, "10.10_information_security_policies"),
    (14385, "10.11_information_security_roles"),
    (14386, "10.12_clean_desk_clear_screen"),
    (14387, "10.13_email_communications"),
    (14388, "10.14_exceptions_to_technology_policies"),
    (14389, "10.15_storage_of_electronic_records"),
    (14390, "10.16_artificial_intelligence"),
]

# Priority 2: Key student-relevant policies
PRIORITY_2 = [
    (14242, "emergency_management"),
    (14246, "weapons_on_university_property"),
    (14247, "tobacco_free_campus"),
    (14269, "hipaa_compliance"),
    (14270, "alcoholic_beverages"),
    (14275, "drug_free_environment"),
    (14317, "hazing"),
    (14245, "title_ix_compliance"),
    (14391, "prohibited_discrimination_and_harassment"),
]

# All BookIds (Priority 4 — scrape any not already covered)
ALL_BOOK_IDS = [
    14283, 14328, 14290, 14293, 14270, 14390, 14319, 14313, 14301, 14267,
    14305, 14306, 14321, 14299, 14386, 14383, 14315, 14264, 14310, 14285,
    14266, 14307, 14275, 14322, 14387, 14242, 14327, 14308, 14297, 14388,
    14309, 14333, 14273, 14329, 14332, 14258, 14302, 14317, 14358, 14269,
    14318, 14291, 14320, 14384, 14385, 14334, 14281, 14272, 14276, 14261,
    14268, 14303, 14382, 14314, 14295, 14286, 14312, 14391, 14323, 14359,
    14311, 14294, 14331, 14271, 14326, 14284, 14287, 14279, 14336, 14316,
    14389, 14330, 14288, 14245, 14247, 14274, 14282, 14292, 14335, 14289,
    14263, 14278, 14300, 14304, 14280, 14337, 14324, 14325, 14246, 14265,
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "X-Requested-With": "XMLHttpRequest",
}

OUTPUT_DIR = "data/policies"


def fetch_all_pages(book_id: int) -> tuple[str, list[str]]:
    """
    Fetches all pages of a policy book using the AJAX API.
    Returns (title, [page_text, ...])
    Follows NextId links until the end of the book.
    """
    title = f"Policy_{book_id}"
    all_text_chunks: list[str] = []
    visited_pages: set[int] = set()
    next_page_id = -1  # -1 = first page

    while True:
        url = CONTENT_API.format(book_id=book_id, page_id=next_page_id)
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()

        data = json.loads(resp.text)

        if not data.get("Success"):
            break

        # Extract title from first page (API returns "Name - Name", deduplicate)
        if next_page_id == -1 and data.get("Title"):
            raw = data["Title"].strip()
            parts = [p.strip() for p in raw.split(" - ")]
            title = parts[0] if len(set(parts)) == 1 else raw

        # Extract text from Pages array
        pages = data.get("Pages", [])
        for page in pages:
            page_id = page.get("PageId")
            if page_id in visited_pages:
                continue
            visited_pages.add(page_id)

            header_html = page.get("Header", "") or ""
            content_html = page.get("Content", "") or ""
            combined_html = header_html + content_html

            if combined_html.strip():
                soup = BeautifulSoup(combined_html, "html.parser")
                text = soup.get_text(separator="\n", strip=True)
                text = re.sub(r"\n{3,}", "\n\n", text)
                all_text_chunks.append(text)

        # Follow to next page if available
        current_page_id = data.get("PageId")
        if current_page_id:
            visited_pages.add(current_page_id)

        next_id = data.get("NextId", 0)
        if not next_id or next_id == 0 or next_id in visited_pages:
            break
        next_page_id = next_id

    return title, all_text_chunks


def save_policy(book_id: int, filename: str, title: str, chunks: list[str]) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, f"{filename}.txt")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"SOURCE: https://faupub.cfmnetwork.com/B.aspx?BookId={book_id}\n")
        f.write(f"TITLE: {title}\n")
        f.write("=" * 60 + "\n\n")
        f.write("\n\n".join(chunks))
    print(f"  Saved: {filepath}  ({sum(len(c) for c in chunks)} chars)")


def scrape_one(book_id: int, filename: str) -> bool:
    filepath = os.path.join(OUTPUT_DIR, f"{filename}.txt")
    if os.path.exists(filepath):
        print(f"  [SKIP] {filename}.txt already exists")
        return True
    try:
        print(f"  Fetching BookId={book_id} -> {filename}.txt ...", end=" ", flush=True)
        title, chunks = fetch_all_pages(book_id)
        if not chunks:
            print("[WARN] No content found")
            return False
        save_policy(book_id, filename, title, chunks)
        return True
    except Exception as e:
        print(f"\n  [ERROR] BookId={book_id}: {e}")
        return False
    finally:
        time.sleep(1.2)


def run_priority(items: list[tuple[int, str]], label: str) -> set[int]:
    print(f"\n{'='*60}\n  {label}\n{'='*60}")
    scraped: set[int] = set()
    for book_id, filename in items:
        if scrape_one(book_id, filename):
            scraped.add(book_id)
    return scraped


def run_remaining(all_ids: list[int], already_scraped: set[int]) -> None:
    remaining = [bid for bid in all_ids if bid not in already_scraped]
    print(f"\n{'='*60}\n  PRIORITY 4 — Remaining {len(remaining)} policies\n{'='*60}")
    for book_id in remaining:
        scrape_one(book_id, f"policy_{book_id}")


if __name__ == "__main__":
    scraped: set[int] = set()
    scraped |= run_priority(PRIORITY_1, "PRIORITY 1 — IT/Security Policies (10.x)")
    scraped |= run_priority(PRIORITY_2, "PRIORITY 2 — Key Student Policies")
    run_remaining(ALL_BOOK_IDS, scraped)
    saved = len([f for f in os.listdir(OUTPUT_DIR) if f.endswith(".txt")])
    print(f"\nDone! {saved} files in {OUTPUT_DIR}/")
