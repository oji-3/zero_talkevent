"""
使い方:
  python scrape_zeropro.py                       # 標準出力にCSV
  python scrape_zeropro.py --save items.csv      # items.csv に保存
  python scrape_zeropro.py --category 5301897    # カテゴリIDを変えたい場合
"""
import re
import csv
import sys
import time
import argparse
from typing import List, Dict
from urllib.parse import urljoin

import requests

SITE = "https://zeroproz2a.base.shop"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# 1ページ目のHTMLを parse_req.py の正規表現イメージで抽出
ITEM_PATTERN = re.compile(
    r'<a\s+class="items-grid_anchor_[^"]*"\s+href="([^"]*)"[^>]*?>'
    r'.*?'
    r'<p\s+class="items-grid_itemTitleText_[^"]*">([^<]*)</p>',
    re.DOTALL
)


def fetch_page1_items(category_id: str, timeout: int = 20) -> List[Dict[str, str]]:
    url = f"{SITE}/categories/{category_id}"
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    html = resp.text

    items = []
    seen = set()

    for m in ITEM_PATTERN.finditer(html):
        href = m.group(1)
        title = (m.group(2) or "").strip()
        full_url = urljoin(SITE, href)

        # URL重複で除外
        if "/items/" in full_url and full_url not in seen:
            items.append({"title": title, "url": full_url})
            seen.add(full_url)

    # 念のためフォールバック（class名が変わった場合でも a[href^="/items/"] を拾う）
    if not items:
        try:
            # 簡易フォールバック: aタグとタイトル近傍をざっくり拾う
            alt = re.findall(
                r'<a[^>]+href="(/items/[^"]+)"[^>]*>(?:\s*<[^>]+>)*\s*([^<]{1,200})',
                html, re.DOTALL
            )
            for href, txt in alt:
                full = urljoin(SITE, href)
                if full not in seen:
                    items.append({"title": " ".join(txt.split()), "url": full})
                    seen.add(full)
        except Exception:
            pass

    return items


def fetch_more_pages(category_id: str, start_page: int = 2, sleep_sec: float = 0.7, timeout: int = 20) -> List[Dict[str, str]]:
    """2ページ目以降は JSON API を n=2 から空/404まで。"""
    results: List[Dict[str, str]] = []
    page = start_page
    tmpl = f"{SITE}/load_items/categories/{category_id}/{{page}}?response_type=json"

    while True:
        url = tmpl.format(page=page)
        r = requests.get(url, headers=HEADERS, timeout=timeout)

        if r.status_code == 404:
            break  # そのページが無い

        r.raise_for_status()

        # 空や不正を安全に判定
        data = None
        try:
            data = r.json()
        except ValueError:
            # JSONでない → 終了
            break

        if not data:
            break  # 空リスト or None → 終了

        for d in data:
            title = (d.get("title") or "").strip()
            href = d.get("url") or ""
            full_url = urljoin(SITE, href)
            if "/items/" in full_url:
                results.append({"title": title, "url": full_url})

        page += 1
        # 連続アクセスにならないよう控えめにスリープ
        time.sleep(sleep_sec)

    return results


def dedup_keep_order(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    seen = set()
    out: List[Dict[str, str]] = []
    for r in rows:
        k = r.get("url")
        if k and k not in seen:
            out.append(r)
            seen.add(k)
    return out


def print_csv(rows: List[Dict[str, str]], fp=sys.stdout):
    writer = csv.DictWriter(fp, fieldnames=["title", "url"])
    writer.writeheader()
    for r in rows:
        writer.writerow(r)


def save_csv(rows: List[Dict[str, str]], filename: str):
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "url"])
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Fetch items and URLs from zeroproz2a.base.shop category.")
    parser.add_argument("--category", default="5301897", help="Category ID (default: 5301897)")
    parser.add_argument("--save", help="Save CSV to file (optional)")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout seconds (default: 20)")
    parser.add_argument("--sleep", type=float, default=0.7, help="Sleep seconds between JSON pages (default: 0.7)")
    args = parser.parse_args()

    try:
        page1 = fetch_page1_items(args.category, timeout=args.timeout)
        more = fetch_more_pages(args.category, start_page=2, sleep_sec=args.sleep, timeout=args.timeout)
        all_rows = dedup_keep_order(page1 + more)

        if args.save:
            save_csv(all_rows, args.save)
        else:
            print_csv(all_rows)

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
