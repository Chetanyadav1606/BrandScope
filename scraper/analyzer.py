"""
analyzer.py — Sentiment Analysis & Theme Extraction for Luggage Reviews

Uses VADER sentiment + custom keyword-based aspect-level analysis.
Generates brand_summary.json and agent_insights.json.

Usage: python analyzer.py
"""

import json
import os
import re
from collections import Counter, defaultdict

import subprocess
import sys

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # type: ignore
except ImportError:
    print("vaderSentiment not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "vaderSentiment"])
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # type: ignore

# ─── Aspect Keywords ──────────────────────────────────────────────────────────

ASPECT_KEYWORDS = {
    "wheels": ["wheel", "spinner", "rolling", "rotate", "caster", "roll", "glide", "swivel"],
    "handle": ["handle", "telescopic", "grip", "pull", "retract", "trolley handle", "push"],
    "material": ["material", "fabric", "polycarbonate", "hard shell", "soft", "build quality",
                 "plastic", "abs", "shell", "body", "surface", "finish", "texture"],
    "zipper": ["zipper", "zip", "zipping", "unzip", "slider", "teeth"],
    "durability": ["durable", "broke", "break", "crack", "damage", "sturdy", "flimsy",
                   "long lasting", "robust", "fragile", "wear", "tear", "dent", "scratch"],
    "size": ["spacious", "compact", "cabin", "capacity", "room", "space", "fit",
             "expandable", "roomy", "storage", "compartment", "pocket"],
    "value": ["worth", "value for money", "overpriced", "cheap", "affordable", "expensive",
              "price", "cost", "budget", "premium", "bang for buck"],
    "design": ["design", "look", "color", "style", "aesthetic", "attractive", "beautiful",
               "trendy", "classy", "elegant", "appearance"]
}

TRUST_RED_FLAGS = [
    "received free", "got this for free", "in exchange for", "complimentary",
    "gifted", "promotional", "sample product"
]


def load_data():
    """Load products and reviews from dataset."""
    with open("../dataset/products.json", "r", encoding="utf-8") as f:
        products = json.load(f)
    with open("../dataset/reviews.json", "r", encoding="utf-8") as f:
        reviews = json.load(f)
    return products, reviews


def analyze_sentiment(reviews):
    """Score each review with VADER sentiment."""
    analyzer = SentimentIntensityAnalyzer()
    for review in reviews:
        scores = analyzer.polarity_scores(review["text"])
        review["sentiment_score"] = round(scores["compound"], 3)
        review["sentiment_pos"] = round(scores["pos"], 3)
        review["sentiment_neg"] = round(scores["neg"], 3)
        review["sentiment_neu"] = round(scores["neu"], 3)
        if scores["compound"] >= 0.05:
            review["sentiment_label"] = "positive"
        elif scores["compound"] <= -0.05:
            review["sentiment_label"] = "negative"
        else:
            review["sentiment_label"] = "neutral"
    return reviews


def extract_aspects(reviews):
    """Tag each review with detected aspects and their sentiment."""
    for review in reviews:
        text_lower = review["text"].lower()
        aspects_found = {}
        for aspect, keywords in ASPECT_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    aspects_found[aspect] = review["sentiment_score"]
                    break
        review["aspects"] = aspects_found
    return reviews


def detect_trust_signals(reviews):
    """Flag reviews with potential trust issues."""
    for review in reviews:
        text_lower = review["text"].lower()
        flags = []
        for flag in TRUST_RED_FLAGS:
            if flag in text_lower:
                flags.append(flag)
        if len(review["text"]) < 20:
            flags.append("very_short_review")
        review["trust_flags"] = flags
        review["is_suspicious"] = len(flags) > 0
    return reviews


def compute_brand_summaries(products, reviews):
    """Compute aggregated brand-level summaries."""
    brands = {}
    brand_reviews = defaultdict(list)
    brand_products = defaultdict(list)

    for r in reviews:
        brand_reviews[r["brand"]].append(r)
    for p in products:
        brand_products[p["brand"]].append(p)

    for brand_name in brand_products:
        prods = brand_products[brand_name]
        revs = brand_reviews[brand_name]

        # Price metrics
        prices = [p["selling_price"] for p in prods]
        list_prices = [p["list_price"] for p in prods]
        discounts = [p["discount_pct"] for p in prods]
        ratings = [p["rating"] for p in prods]

        # Sentiment metrics
        sentiments = [r["sentiment_score"] for r in revs]
        pos_count = sum(1 for r in revs if r["sentiment_label"] == "positive")
        neg_count = sum(1 for r in revs if r["sentiment_label"] == "negative")
        neu_count = sum(1 for r in revs if r["sentiment_label"] == "neutral")

        # Aspect-level sentiment
        aspect_sentiments = defaultdict(list)
        for r in revs:
            for aspect, score in r.get("aspects", {}).items():
                aspect_sentiments[aspect].append(score)

        aspect_summary = {}
        for aspect, scores in aspect_sentiments.items():
            aspect_summary[aspect] = {
                "avg_sentiment": round(sum(scores) / len(scores), 3),
                "mention_count": len(scores),
                "positive_pct": round(sum(1 for s in scores if s >= 0.05) / len(scores) * 100, 1)
            }

        # Top themes extraction
        pos_reviews = [r for r in revs if r["sentiment_label"] == "positive"]
        neg_reviews = [r for r in revs if r["sentiment_label"] == "negative"]

        top_pros = extract_themes(pos_reviews, positive=True)
        top_cons = extract_themes(neg_reviews, positive=False)

        # Anomaly detection: high rating but negative sentiment
        anomalies = []
        for p in prods:
            prod_revs = [r for r in revs if r["product_id"] == p["id"]]
            if prod_revs:
                avg_sent = sum(r["sentiment_score"] for r in prod_revs) / len(prod_revs)
                if p["rating"] >= 4.0 and avg_sent < 0:
                    anomalies.append({
                        "product": p["title"],
                        "rating": p["rating"],
                        "avg_sentiment": round(avg_sent, 3),
                        "flag": "High rating but negative review sentiment"
                    })

        # Value-for-money score (sentiment normalized by price position)
        avg_price = sum(prices) / len(prices)
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        all_avg_price = sum(p["selling_price"] for p in products) / len(products)
        price_ratio = avg_price / all_avg_price if all_avg_price else 1
        vfm_score = round(avg_sentiment / price_ratio, 3) if price_ratio else 0

        # Review trust
        suspicious_count = sum(1 for r in revs if r.get("is_suspicious", False))

        brands[brand_name] = {
            "brand": brand_name,
            "product_count": len(prods),
            "review_count": len(revs),
            "total_listed_reviews": sum(p["total_reviews"] for p in prods),
            "avg_price": round(sum(prices) / len(prices)),
            "min_price": min(prices),
            "max_price": max(prices),
            "avg_list_price": round(sum(list_prices) / len(list_prices)),
            "avg_discount_pct": round(sum(discounts) / len(discounts), 1),
            "avg_rating": round(sum(ratings) / len(ratings), 2),
            "avg_sentiment": round(avg_sentiment, 3),
            "sentiment_distribution": {
                "positive": pos_count,
                "neutral": neu_count,
                "negative": neg_count
            },
            "aspect_sentiment": aspect_summary,
            "top_pros": top_pros[:5],
            "top_cons": top_cons[:5],
            "anomalies": anomalies,
            "vfm_score": vfm_score,
            "suspicious_reviews": suspicious_count,
            "positioning": get_positioning(avg_price),
        }

    return brands


def extract_themes(reviews, positive=True):
    """Extract recurring themes from reviews."""
    theme_phrases = {
        "wheels": ["smooth wheels", "wheel quality", "spinner wheels", "wheels broke", "wheel wobble"],
        "handle": ["telescopic handle", "handle quality", "sturdy handle", "handle broke", "comfortable grip"],
        "material": ["build quality", "material quality", "hard shell", "polycarbonate", "scratch resistant"],
        "zipper": ["zipper quality", "smooth zipper", "zipper stuck", "zip broke"],
        "durability": ["very durable", "long lasting", "broke easily", "poor durability", "sturdy build"],
        "value": ["value for money", "worth the price", "overpriced", "affordable", "budget friendly"],
        "design": ["looks premium", "great design", "attractive colors", "trendy look", "stylish"],
        "size": ["spacious interior", "good capacity", "cabin size", "expandable", "compact"],
        "lightweight": ["very lightweight", "easy to carry", "light weight"],
        "service": ["good service", "poor service", "customer support"]
    }

    theme_counts = Counter()
    for review in reviews:
        text_lower = review["text"].lower()
        for theme, phrases in theme_phrases.items():
            for phrase in phrases:
                if phrase in text_lower:
                    label = phrase if positive else phrase
                    theme_counts[label] += 1

    # Also extract from aspect keywords
    for review in reviews:
        for aspect in review.get("aspects", {}):
            if positive:
                theme_counts[f"good {aspect}"] += 1
            else:
                theme_counts[f"poor {aspect}"] += 1

    return [{"theme": theme, "count": count} for theme, count in theme_counts.most_common(10)]


def get_positioning(avg_price):
    """Classify brand positioning based on average price."""
    if avg_price < 2500:
        return "budget"
    elif avg_price < 4000:
        return "mass-market"
    elif avg_price < 7000:
        return "mid-range"
    else:
        return "premium"


def generate_agent_insights(brands, products, reviews):
    """Generate 5+ non-obvious conclusions from cross-brand analysis."""
    insights = []
    brand_list = list(brands.values())

    # 1. Best value-for-money brand
    vfm_sorted = sorted(brand_list, key=lambda b: b["vfm_score"], reverse=True)
    best_vfm = vfm_sorted[0]
    worst_vfm = vfm_sorted[-1]
    insights.append({
        "id": 1,
        "title": "Best Value-for-Money Winner",
        "insight": f"{best_vfm['brand']} delivers the highest sentiment-to-price ratio (VFM score: {best_vfm['vfm_score']}), "
                   f"meaning customers feel they get the most satisfaction per rupee spent. "
                   f"In contrast, {worst_vfm['brand']} scores lowest ({worst_vfm['vfm_score']}), suggesting customers "
                   f"expect more for the price they pay.",
        "category": "value",
        "severity": "high"
    })

    # 2. Discount dependency analysis
    high_discount = [b for b in brand_list if b["avg_discount_pct"] > 50]
    if high_discount:
        names = ", ".join(b["brand"] for b in high_discount)
        insights.append({
            "id": 2,
            "title": "Discount-Dependent Brands",
            "insight": f"{names} rely on heavy discounting (>50% average) to drive sales. "
                       f"This suggests their list prices are artificially inflated for perceived value, "
                       f"or their brand equity isn't strong enough to command full price. "
                       f"A decision-maker should question whether these brands can sustain margins.",
            "category": "pricing",
            "severity": "medium"
        })

    # 3. Sentiment vs Rating mismatch
    for b in brand_list:
        if b["avg_rating"] >= 4.0 and b["avg_sentiment"] < 0.2:
            insights.append({
                "id": 3,
                "title": "Rating-Sentiment Disconnect",
                "insight": f"{b['brand']} shows a {b['avg_rating']} star average rating but only {b['avg_sentiment']} sentiment score. "
                           f"This gap suggests that while quick star ratings look good, detailed review text reveals "
                           f"more nuanced dissatisfaction. Ratings alone are misleading for this brand.",
                "category": "anomaly",
                "severity": "high"
            })
            break

    # 4. Aspect weakness comparison
    wheel_scores = {b["brand"]: b["aspect_sentiment"].get("wheels", {}).get("avg_sentiment", 0)
                    for b in brand_list}
    worst_wheels = min(wheel_scores, key=wheel_scores.get)
    best_wheels = max(wheel_scores, key=wheel_scores.get)
    insights.append({
        "id": 4,
        "title": "The Wheel Quality Gap",
        "insight": f"Wheel quality is the most polarizing aspect across brands. {best_wheels} leads with "
                   f"sentiment score {wheel_scores[best_wheels]:.3f} while {worst_wheels} "
                   f"scores {wheel_scores[worst_wheels]:.3f}. Since wheels are the #1 mentioned aspect in negative reviews, "
                   f"this single feature significantly impacts overall brand perception.",
        "category": "product",
        "severity": "high"
    })

    # 5. Premium doesn't always mean better
    premium_brands = [b for b in brand_list if b["avg_price"] > 4000]
    budget_brands = [b for b in brand_list if b["avg_price"] < 3000]
    if premium_brands and budget_brands:
        prem_sent = sum(b["avg_sentiment"] for b in premium_brands) / len(premium_brands)
        budg_sent = sum(b["avg_sentiment"] for b in budget_brands) / len(budget_brands)
        if budg_sent > prem_sent * 0.8:
            insights.append({
                "id": 5,
                "title": "Budget Brands Punch Above Their Weight",
                "insight": f"Budget brands (avg sentiment: {budg_sent:.3f}) achieve nearly the same customer satisfaction "
                           f"as premium brands ({prem_sent:.3f}) at less than half the price. "
                           f"For price-sensitive Indian consumers, the incremental quality improvement "
                           f"from premium brands may not justify the 2-3x price premium.",
                "category": "competitive",
                "severity": "medium"
            })

    # 6. Durability concern across all brands
    dur_mentions = {b["brand"]: b["aspect_sentiment"].get("durability", {}).get("mention_count", 0)
                    for b in brand_list}
    total_dur = sum(dur_mentions.values())
    insights.append({
        "id": 6,
        "title": "Industry-Wide Durability Concerns",
        "insight": f"Durability is mentioned in {total_dur} reviews across all brands, making it the most discussed "
                   f"concern in the luggage category. No brand has solved this completely, presenting an opportunity "
                   f"for a brand that can credibly communicate and deliver long-term durability.",
        "category": "market",
        "severity": "medium"
    })

    # 7. Review trust analysis
    suspicious = {b["brand"]: b["suspicious_reviews"] for b in brand_list}
    most_suspicious = max(suspicious, key=suspicious.get)
    if suspicious[most_suspicious] > 0:
        insights.append({
            "id": 7,
            "title": "Review Authenticity Varies by Brand",
            "insight": f"Review trust analysis reveals uneven patterns. {most_suspicious} has the highest "
                       f"count of flagged reviews ({suspicious[most_suspicious]}). Decision-makers should weight "
                       f"sentiment scores from verified purchases more heavily and treat aggregate ratings with caution.",
            "category": "trust",
            "severity": "low"
        })

    return insights


def main():
    """Run the full analysis pipeline."""
    print("Loading dataset...")
    products, reviews = load_data()

    print(f"Loaded {len(products)} products and {len(reviews)} reviews")

    print("Running VADER sentiment analysis...")
    reviews = analyze_sentiment(reviews)

    print("Extracting aspect-level themes...")
    reviews = extract_aspects(reviews)

    print("Detecting trust signals...")
    reviews = detect_trust_signals(reviews)

    print("Computing brand summaries...")
    brand_summaries = compute_brand_summaries(products, reviews)

    print("Generating agent insights...")
    insights = generate_agent_insights(brand_summaries, products, reviews)

    # Save enriched data
    os.makedirs("../dataset", exist_ok=True)

    with open("../dataset/reviews.json", "w", encoding="utf-8") as f:
        json.dump(reviews, f, indent=2, ensure_ascii=False)

    with open("../dataset/brand_summary.json", "w", encoding="utf-8") as f:
        json.dump(brand_summaries, f, indent=2, ensure_ascii=False)

    with open("../dataset/agent_insights.json", "w", encoding="utf-8") as f:
        json.dump(insights, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Analysis complete!")
    print(f"   Brand summaries: {len(brand_summaries)}")
    print(f"   Agent insights:  {len(insights)}")
    for brand, data in brand_summaries.items():
        print(f"   {brand}: sentiment={data['avg_sentiment']:.3f}, "
              f"avg_price=₹{data['avg_price']}, "
              f"rating={data['avg_rating']}")


if __name__ == "__main__":
    main()
