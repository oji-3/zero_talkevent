import re
import csv
import sys

def parse_html_items():
    with open("response.txt", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract product information pattern
    item_pattern = r'<a class="items-grid_anchor_[^"]*" href="([^"]*)"[^>]*>.*?<p class="items-grid_itemTitleText_[^"]*">([^<]*)</p>'
    
    items = []
    for match in re.finditer(item_pattern, content, re.DOTALL):
        url = match.group(1)
        title = match.group(2).strip()
        items.append({"title": title, "url": url})
    
    return items

if __name__ == "__main__":
    items = parse_html_items()
    
    writer = csv.DictWriter(sys.stdout, fieldnames=["title", "url"])
    writer.writeheader()
    for item in items:
        writer.writerow(item)