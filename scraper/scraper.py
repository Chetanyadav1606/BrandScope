"""
scraper.py — Amazon India Luggage Product & Review Scraper

Uses Playwright with stealth techniques to scrape product listings and reviews.
Due to Amazon's anti-bot measures, success may vary. Use generate_dataset.py as fallback.

Usage:
    pip install playwright
    python -m playwright install chromium
    python scraper.py

Output:
    data/products_raw.json
    data/reviews_raw.json
"""

import json
import os
import re
import time
import random
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed. Run: pip install playwright && python -m playwright install chromium")
    exit(1)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing beautifulsoup4...")
    os.system("pip install beautifulsoup4")
    from bs4 import BeautifulSoup

# ─── Configuration ─────────────────────────────────────────────────────────────

BRANDS = ["Safari", "Skybags", "American Tourister", "VIP", "Aristocrat", "Nasher Miles"]
PRODUCTS_PER_BRAND = 12
REVIEWS_PER_PRODUCT = 8
BASE_URL = "https://www.amazon.in"
SEARCH_URL = BASE_URL + "/s?k={query}+luggage+trolley+bag&ref=nb_sb_noss"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

os.makedirs("data", exist_ok=True)


def random_delay(min_s=2, max_s=5):
    """Add a random delay to mimic human behavior."""
    time.sleep(random.uniform(min_s, max_s))


def parse_price(text):
    """Extract numeric price from text like '₹2,499' or '2,499.00'."""
    if not text:
        return 0
    nums = re.findall(r'[\d,]+\.?\d*', text.replace(',', ''))
    return int(float(nums[0])) if nums else 0


def scrape_search_results(page, brand):
    """Scrape product listings from search results page."""
    url = SEARCH_URL.format(query=brand.replace(" ", "+"))
    print(f"  Searching: {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    random_delay(3, 6)

    products = []
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    # Find product cards
    items = soup.select('[data-component-type="s-search-result"]')
    print(f"  Found {len(items)} search results")

    for item in items[:PRODUCTS_PER_BRAND]:
        try:
            # ASIN
            asin = item.get("data-asin", "")
            if not asin:
                continue

            # Title
            title_el = item.select_one("h2 a span") or item.select_one("h2 span")
            title = title_el.get_text(strip=True) if title_el else ""
            if not title or brand.lower() not in title.lower():
                continue

            # Price
            price_whole = item.select_one(".a-price-whole")
            selling_price = parse_price(price_whole.get_text(strip=True)) if price_whole else 0

            # List price
            list_price_el = item.select_one(".a-price.a-text-price .a-offscreen")
            list_price = parse_price(list_price_el.get_text(strip=True)) if list_price_el else selling_price

            # Rating
            rating_el = item.select_one(".a-icon-alt")
            rating_text = rating_el.get_text(strip=True) if rating_el else "0"
            rating = float(re.findall(r'[\d.]+', rating_text)[0]) if re.findall(r'[\d.]+', rating_text) else 0

            # Review count
            review_el = item.select_one('a[href*="#customerReviews"] span') or item.select_one('.a-size-base.s-underline-text')
            review_count = parse_price(review_el.get_text(strip=True)) if review_el else 0

            # Product URL
            link_el = item.select_one("h2 a")
            product_url = BASE_URL + link_el["href"] if link_el and link_el.get("href") else ""

            # Discount
            discount_pct = round((1 - selling_price / list_price) * 100) if list_price > selling_price else 0

            # Category detection
            title_lower = title.lower()
            category = "cabin"
            if "set" in title_lower:
                category = "set"
            elif any(s in title_lower for s in ["75", "76", "77", "78", "79", "large"]):
                category = "large"
            elif any(s in title_lower for s in ["65", "66", "67", "68", "69", "medium"]):
                category = "medium"

            # Size extraction
            size_match = re.search(r'(\d{2})\s*cm', title_lower)
            size_cm = int(size_match.group(1)) if size_match else 0

            product = {
                "asin": asin,
                "brand": brand,
                "title": title,
                "category": category,
                "size_cm": size_cm,
                "selling_price": selling_price,
                "list_price": list_price,
                "discount_pct": discount_pct,
                "rating": rating,
                "total_reviews": review_count,
                "url": product_url,
            }
            products.append(product)
            print(f"    ✓ {title[:60]}... ₹{selling_price}")

        except Exception as e:
            print(f"    ✗ Error parsing product: {e}")
            continue

    return products


def scrape_reviews(page, product):
    """Scrape reviews for a single product."""
    url = product.get("url", "")
    if not url:
        return []

    reviews = []
    try:
        print(f"    Fetching reviews for: {product['title'][:50]}...")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        random_delay(2, 4)

        # Click "See all reviews" link if exists
        try:
            see_all = page.locator('a[data-hook="see-all-reviews-link-foot"]')
            if see_all.count() > 0:
                see_all.first.click()
                random_delay(2, 4)
        except:
            pass

        html = page.content()
        soup = BeautifulSoup(html, "html.parser")

        review_divs = soup.select('[data-hook="review"]')
        for rev in review_divs[:REVIEWS_PER_PRODUCT]:
            try:
                # Rating
                rating_el = rev.select_one('[data-hook="review-star-rating"] .a-icon-alt')
                rating = 0
                if rating_el:
                    r = re.findall(r'[\d.]+', rating_el.get_text())
                    rating = int(float(r[0])) if r else 0

                # Title
                title_el = rev.select_one('[data-hook="review-title"] span:last-child')
                title = title_el.get_text(strip=True) if title_el else ""

                # Body
                body_el = rev.select_one('[data-hook="review-body"] span')
                body = body_el.get_text(strip=True) if body_el else ""

                # Date
                date_el = rev.select_one('[data-hook="review-date"]')
                date_text = date_el.get_text(strip=True) if date_el else ""
                date = datetime.now().strftime("%Y-%m-%d")

                # Verified
                verified_el = rev.select_one('[data-hook="avp-badge"]')
                verified = verified_el is not None

                # Reviewer
                author_el = rev.select_one('.a-profile-name')
                author = author_el.get_text(strip=True) if author_el else "Amazon Customer"

                if body:
                    reviews.append({
                        "product_asin": product["asin"],
                        "brand": product["brand"],
                        "product_title": product["title"],
                        "reviewer_name": author,
                        "rating": rating,
                        "title": title,
                        "text": body,
                        "date": date,
                        "verified_purchase": verified,
                    })
            except Exception as e:
                continue

    except Exception as e:
        print(f"    ✗ Error fetching reviews: {e}")

    print(f"    Got {len(reviews)} reviews")
    return reviews


def main():
    """Run the full scraping pipeline."""
    print("=" * 60)
    print("Amazon India Luggage Scraper")
    print("=" * 60)
    print(f"Brands: {', '.join(BRANDS)}")
    print(f"Products per brand: {PRODUCTS_PER_BRAND}")
    print()

    all_products = []
    all_reviews = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={'width': 1366, 'height': 768},
            locale='en-IN',
        )
        page = context.new_page()

        # Block unnecessary resources
        page.route("**/*.{png,jpg,jpeg,gif,svg,ico,woff,woff2}", lambda route: route.abort())

        for brand in BRANDS:
            print(f"\n{'─' * 40}")
            print(f"Scraping: {brand}")
            print(f"{'─' * 40}")

            products = scrape_search_results(page, brand)
            all_products.extend(products)

            for product in products[:PRODUCTS_PER_BRAND]:
                reviews = scrape_reviews(page, product)
                all_reviews.extend(reviews)
                random_delay(2, 5)

        browser.close()

    # Assign IDs
    for i, p in enumerate(all_products):
        p["id"] = i + 1
    for i, r in enumerate(all_reviews):
        r["id"] = i + 1
        # Map product_id from ASIN
        for p in all_products:
            if p["asin"] == r.get("product_asin"):
                r["product_id"] = p["id"]
                break

    # Save
    with open("data/products_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)
    with open("data/reviews_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"Scraping complete!")
    print(f"Products: {len(all_products)}")
    print(f"Reviews:  {len(all_reviews)}")
    print(f"Output:   data/products_raw.json, data/reviews_raw.json")
    print(f"\nNext step: Run analyzer.py to process the scraped data")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
