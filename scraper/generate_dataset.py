"""
generate_dataset.py — Realistic Dataset Generator for Amazon India Luggage Brands

Generates a structured, realistic dataset based on real Amazon India market data patterns.
Covers 6 brands × 12+ products × 60+ reviews per brand.

Usage:
    python generate_dataset.py

Output:
    ../dataset/products.json
    ../dataset/reviews.json
"""

import json
import random
import os
import math
from datetime import datetime, timedelta

random.seed(42)

# ─── Brand Profiles (based on real Amazon India market data) ───────────────────

BRAND_PROFILES = {
    "Safari": {
        "price_range": (1299, 4999),
        "avg_discount_pct": 55,
        "rating_mean": 3.8,
        "rating_std": 0.5,
        "review_count_range": (800, 25000),
        "positioning": "mass-market",
        "strengths": ["affordable", "lightweight", "value for money", "spacious interiors", "decent build quality"],
        "weaknesses": ["wheel quality degrades quickly", "zipper gets stuck", "handle feels flimsy", "color fades after use", "scratches easily"],
        "product_lines": [
            ("Safari Pentagon 55 Cabin Luggage", "cabin", 55),
            ("Safari Thorium Sharp 66 Medium Check-in", "medium", 66),
            ("Safari Thorium Sharp 77 Large Check-in", "large", 77),
            ("Safari Crypto 55 Cabin Hard Luggage", "cabin", 55),
            ("Safari Crypto 65 Medium Hard Luggage", "medium", 65),
            ("Safari Harbour 55 Cabin Trolley", "cabin", 55),
            ("Safari Pentagon 66 Medium Trolley Bag", "medium", 66),
            ("Safari Flo Secure 4W 55 Cabin Suitcase", "cabin", 55),
            ("Safari Regloss Antiscratch 76 Large", "large", 76),
            ("Safari Thorium Neo 55 Cabin Luggage", "cabin", 55),
            ("Safari Pentagon Set of 3 (S/M/L)", "set", 0),
            ("Safari Flo Secure 4W 69 Medium Trolley", "medium", 69),
        ]
    },
    "Skybags": {
        "price_range": (1499, 5999),
        "avg_discount_pct": 50,
        "rating_mean": 3.9,
        "rating_std": 0.4,
        "review_count_range": (500, 18000),
        "positioning": "mass-market",
        "strengths": ["trendy designs", "good color options", "smooth wheels", "lightweight", "sturdy locks"],
        "weaknesses": ["material scratches easily", "handle gets wobbly", "zip quality average", "dents on impact", "customer service slow"],
        "product_lines": [
            ("Skybags Trooper 55 Cabin Hard Luggage", "cabin", 55),
            ("Skybags Trooper 65 Medium Hard Luggage", "medium", 65),
            ("Skybags Trooper 75 Large Hard Luggage", "large", 75),
            ("Skybags Brat 55 Cabin Trolley", "cabin", 55),
            ("Skybags Brat 68 Medium Trolley", "medium", 68),
            ("Skybags Rubik 55 Cabin Spinner", "cabin", 55),
            ("Skybags Rubik 68 Medium Spinner", "medium", 68),
            ("Skybags Marvel Spiderman 55 Cabin", "cabin", 55),
            ("Skybags Neo 55 Cabin Trolley Bag", "cabin", 55),
            ("Skybags Skysurf 55 Cabin Hard Body", "cabin", 55),
            ("Skybags Set of 3 Polycarbonate (S/M/L)", "set", 0),
            ("Skybags Ignite Strolly 78 Large", "large", 78),
        ]
    },
    "American Tourister": {
        "price_range": (2999, 12999),
        "avg_discount_pct": 40,
        "rating_mean": 4.2,
        "rating_std": 0.3,
        "review_count_range": (1000, 45000),
        "positioning": "mid-range",
        "strengths": ["excellent build quality", "very durable wheels", "premium feel", "smooth telescopic handle", "good after-sales service", "trusted brand"],
        "weaknesses": ["expensive compared to alternatives", "heavier than competitors", "limited color options", "scratches visible on dark colors", "basic interior organization"],
        "product_lines": [
            ("American Tourister Ivy 55 Cabin Polypropylene", "cabin", 55),
            ("American Tourister Ivy 68 Medium Check-in", "medium", 68),
            ("American Tourister Ivy 77 Large Check-in", "large", 77),
            ("American Tourister Liftoff 55 Cabin Spinner", "cabin", 55),
            ("American Tourister Liftoff 68 Medium Spinner", "medium", 68),
            ("American Tourister Speedair 55 Cabin Hard", "cabin", 55),
            ("American Tourister Turito 55 Cabin Lightweight", "cabin", 55),
            ("American Tourister Cruze 55 Cabin Trolley", "cabin", 55),
            ("American Tourister Georgia 55 Cabin Polycarbonate", "cabin", 55),
            ("American Tourister Ivy Set of 3 (S/M/L)", "set", 0),
            ("American Tourister Splash 68 Medium Check-in", "medium", 68),
            ("American Tourister Apex 77 Large Check-in", "large", 77),
        ]
    },
    "VIP": {
        "price_range": (1599, 5499),
        "avg_discount_pct": 52,
        "rating_mean": 3.7,
        "rating_std": 0.5,
        "review_count_range": (300, 12000),
        "positioning": "mass-market",
        "strengths": ["very affordable", "lightweight", "decent capacity", "good for budget travelers", "widely available"],
        "weaknesses": ["wheels break easily", "build quality inconsistent", "flimsy handles", "poor scratch resistance", "zipper quality below average"],
        "product_lines": [
            ("VIP Bravo 55 Cabin Polypropylene Trolley", "cabin", 55),
            ("VIP Bravo 69 Medium Check-in Trolley", "medium", 69),
            ("VIP Bravo 79 Large Check-in Trolley", "large", 79),
            ("VIP Zumba 55 Cabin Hard Luggage", "cabin", 55),
            ("VIP Zumba 65 Medium Hard Luggage", "medium", 65),
            ("VIP Xion 56 Cabin Hard Body Luggage", "cabin", 56),
            ("VIP Graphite 55 Cabin Hard Shell", "cabin", 55),
            ("VIP Fairway 69 Medium Soft Trolley", "medium", 69),
            ("VIP Tube NXT 55 Cabin Trolley Bag", "cabin", 55),
            ("VIP Trio Set of 3 (S/M/L)", "set", 0),
            ("VIP Xion 75 Large Hard Body Luggage", "large", 75),
            ("VIP Proton 55 Cabin Spinner Trolley", "cabin", 55),
        ]
    },
    "Aristocrat": {
        "price_range": (1199, 4499),
        "avg_discount_pct": 58,
        "rating_mean": 3.6,
        "rating_std": 0.6,
        "review_count_range": (200, 10000),
        "positioning": "budget",
        "strengths": ["cheapest option", "lightweight", "basic features work", "good entry-level choice", "variety of sizes"],
        "weaknesses": ["poor durability", "wheels wobble after months", "handle telescoping mechanism fails", "material feels cheap", "zipper breaks frequently"],
        "product_lines": [
            ("Aristocrat Air Pro 55 Cabin Hard Trolley", "cabin", 55),
            ("Aristocrat Air Pro 66 Medium Hard Trolley", "medium", 66),
            ("Aristocrat Air Pro 76 Large Hard Trolley", "large", 76),
            ("Aristocrat Juke 55 Cabin Polycarbonate", "cabin", 55),
            ("Aristocrat Juke 67 Medium Polycarbonate", "medium", 67),
            ("Aristocrat Craft 55 Cabin Soft Trolley", "cabin", 55),
            ("Aristocrat Photon 55 Cabin Hard Luggage", "cabin", 55),
            ("Aristocrat Aston 55 Cabin Spinner", "cabin", 55),
            ("Aristocrat Paramount 67 Medium Check-in", "medium", 67),
            ("Aristocrat Air Pro Set of 3 (S/M/L)", "set", 0),
            ("Aristocrat Crystal 55 Cabin Hard Body", "cabin", 55),
            ("Aristocrat Aston 75 Large Check-in Spinner", "large", 75),
        ]
    },
    "Nasher Miles": {
        "price_range": (2499, 9999),
        "avg_discount_pct": 45,
        "rating_mean": 4.0,
        "rating_std": 0.4,
        "review_count_range": (400, 15000),
        "positioning": "premium-value",
        "strengths": ["premium design and finish", "excellent material quality", "smooth silent wheels", "sturdy handles", "good polycarbonate build", "modern aesthetic"],
        "weaknesses": ["higher price point", "limited brand awareness", "fewer service centers", "weight slightly above average", "scratches on glossy variants"],
        "product_lines": [
            ("Nasher Miles Rome 55 Cabin Hard-Sided Polycarbonate", "cabin", 55),
            ("Nasher Miles Rome 65 Medium Hard-Sided", "medium", 65),
            ("Nasher Miles Rome 75 Large Hard-Sided", "large", 75),
            ("Nasher Miles Istanbul 55 Cabin Trolley", "cabin", 55),
            ("Nasher Miles Istanbul 65 Medium Trolley", "medium", 65),
            ("Nasher Miles Paris 55 Cabin Polycarbonate", "cabin", 55),
            ("Nasher Miles Tokyo 55 Cabin Hard Case", "cabin", 55),
            ("Nasher Miles London 55 Cabin Spinner", "cabin", 55),
            ("Nasher Miles Dallas 65 Medium Check-in", "medium", 65),
            ("Nasher Miles Rome Set of 3 (S/M/L)", "set", 0),
            ("Nasher Miles Milan 55 Cabin Hard Shell", "cabin", 55),
            ("Nasher Miles Berlin 75 Large Check-in", "large", 75),
        ]
    }
}

# ─── Review Templates (realistic Amazon India review patterns) ─────────────────

POSITIVE_REVIEW_TEMPLATES = [
    "Excellent {product_type}! {strength}. {detail}. Would definitely recommend to anyone looking for a reliable suitcase.",
    "Very happy with this purchase. {strength}. {detail}. The {aspect} is particularly impressive for this price range.",
    "Great value for money. {strength}. Used it for two trips already and it still looks brand new. {detail}.",
    "Bought this for my {trip_type} and it performed really well. {strength}. {detail}.",
    "{strength}. I was skeptical about ordering luggage online but this exceeded my expectations. {detail}.",
    "Perfect cabin size luggage. {strength}. Fits easily in the overhead compartment. {detail}.",
    "The quality is surprisingly good for the price. {strength}. {detail}. Five stars from me!",
    "Been using this for {months} months now and very satisfied. {strength}. {detail}. No complaints so far.",
    "Received the product in perfect condition. {strength}. {detail}. Amazon delivery was also quick.",
    "Compared several brands before buying this one. {strength}. {detail}. Made the right choice!",
    "My family bought {count} of these for our vacation. {strength}. {detail}. Everyone loved them.",
    "Upgraded from a cheaper brand and the difference is noticeable. {strength}. {detail}.",
    "The {aspect} is really smooth and works perfectly. {strength}. {detail}. Worth every rupee.",
    "Solid build quality. {strength}. Used it on a rough Indian Railways journey and not a scratch. {detail}.",
    "This is my third purchase from this brand and they never disappoint. {strength}. {detail}.",
]

NEGATIVE_REVIEW_TEMPLATES = [
    "Disappointed with the quality. {weakness}. {detail}. Expected better for the price.",
    "{weakness}. Only used it {count} times and already facing issues. {detail}. Not worth the money.",
    "The {aspect} broke within {months} months of purchase. {weakness}. {detail}. Very poor quality.",
    "Looks good initially but {weakness}. {detail}. Will not buy from this brand again.",
    "Not recommended. {weakness}. {detail}. The product photos on Amazon are misleading.",
    "Received a {defect} product. {weakness}. {detail}. Had to go through the hassle of return.",
    "{weakness}. For this price, I expected much better quality. {detail}. Very disappointing experience.",
    "The build quality is subpar. {weakness}. {detail}. My older cheaper suitcase lasted longer.",
    "Bought this based on reviews but regret it. {weakness}. {detail}. Reviews seem fake.",
    "{weakness}. Customer service was also unhelpful when I raised a complaint. {detail}.",
]

MIXED_REVIEW_TEMPLATES = [
    "Decent product for the price. {strength} but {weakness}. {detail}. It's okay for occasional use.",
    "Mixed feelings about this one. {strength}. However, {weakness}. {detail}. Average product overall.",
    "Pros: {strength}. Cons: {weakness}. {detail}. Three stars - it's adequate but nothing special.",
    "Good for short trips. {strength}. But {weakness}. {detail}. You get what you pay for I guess.",
    "The {aspect_good} is great but the {aspect_bad} needs improvement. {detail}. Decent value though.",
    "It's fine for the price range. {strength}. On the downside, {weakness}. {detail}.",
    "Looks premium from outside but {weakness}. {strength} though, so it balances out. {detail}.",
    "Used it for one trip so far. {strength}. {weakness}. {detail}. Will update review after more use.",
]

DETAIL_FRAGMENTS = [
    "The color is exactly as shown in the pictures",
    "Packing was done very well by Amazon",
    "Delivery was within 3 days which was great",
    "My friend also bought the same one after seeing mine",
    "The interior lining is of decent quality",
    "Comes with a combination lock which is handy",
    "The four wheels make it very easy to maneuver in airports",
    "Weight is quite manageable even when fully packed",
    "The expansion zipper adds extra capacity when needed",
    "The side handle is comfortable to grip",
    "I carry this for weekly business travel",
    "Perfect for a 5-7 day trip with careful packing",
    "The finish gives it a classy look",
    "It survived the rough baggage handling at Indian airports",
    "TSA-compatible lock is a nice addition",
    "Interior organizer pockets are really useful",
    "Easy to spot on the baggage carousel due to the unique color",
    "Fits perfectly in train upper berth storage",
    "Dimensions are airline compliant for most domestic carriers",
    "Good balance between weight and durability",
]

ASPECTS = ["wheels", "handle", "material", "zipper", "build quality", "design", "size", "weight"]
TRIP_TYPES = ["business trip to Bangalore", "family vacation to Goa", "Europe trip", "domestic flight to Delhi",
              "week-long holiday", "college trip", "wedding travel", "Rajasthan tour"]

ASPECT_POSITIVE_DETAILS = {
    "wheels": ["The 360-degree spinner wheels are buttery smooth", "Wheels roll effortlessly on all surfaces",
               "The double wheels provide excellent stability", "Wheels are silent even on rough airport floors"],
    "handle": ["The telescopic handle extends and retracts smoothly", "Handle has a comfortable rubber grip",
               "Multi-position handle lock works perfectly", "The push-down handle mechanism is solid"],
    "material": ["The polycarbonate shell feels premium and sturdy", "Hard shell material is scratch-resistant",
                 "Material quality is excellent for the price", "The outer texture hides scratches well"],
    "zipper": ["Zippers are smooth and heavy-duty", "YKK-quality zippers that glide easily",
               "The main zipper has never gotten stuck", "Double zipper closure feels very secure"],
    "durability": ["Still looks new after multiple trips", "Survived rough baggage handling without any damage",
                   "No dents or cracks after 6 months of use", "The corners are well-reinforced"],
    "size": ["Very spacious interior with great organization", "Perfect cabin size - fits airline dimensions exactly",
             "Expandable compartment adds 20% more space", "The depth is ideal for packing suits and formal wear"],
}

ASPECT_NEGATIVE_DETAILS = {
    "wheels": ["One wheel started wobbling after just 2 uses", "Wheels make a terrible rattling noise",
               "The wheel broke off during my first trip", "Wheels got stuck and don't spin freely anymore"],
    "handle": ["The telescopic handle got stuck halfway", "Handle is very wobbly and feels cheap",
               "The retraction mechanism broke within a month", "Handle grip came off during travel"],
    "material": ["The polycarbonate is very thin and flimsy", "Material cracked on first impact",
                 "Surface scratches incredibly easily", "The shell dented just from normal baggage handling"],
    "zipper": ["Zipper teeth separated after light use", "The main zipper gets stuck constantly",
               "Zipper slider broke off on second trip", "Very cheap quality zippers that jam frequently"],
    "durability": ["Started falling apart within weeks", "Multiple parts broke during first trip",
                   "Not durable at all - cracks appeared on corners", "Build quality is atrocious for the price"],
    "size": ["Much smaller than what the dimensions suggest", "Internal space is wasted by thick walls",
             "Doesn't actually fit airline cabin size requirements", "Very limited packing space for the external size"],
}


def generate_price(brand_profile, category):
    """Generate realistic price based on brand profile and product category."""
    low, high = brand_profile["price_range"]
    if category == "cabin":
        base = random.uniform(low, low + (high - low) * 0.4)
    elif category == "medium":
        base = random.uniform(low + (high - low) * 0.3, low + (high - low) * 0.7)
    elif category == "large":
        base = random.uniform(low + (high - low) * 0.5, high)
    elif category == "set":
        base = random.uniform(low + (high - low) * 0.7, high * 1.8)
    else:
        base = random.uniform(low, high)

    # Round to nearest 99
    return round(base / 100) * 100 - 1


def generate_list_price(selling_price, avg_discount):
    """Generate list price based on selling price and discount pattern."""
    discount_pct = max(10, min(75, random.gauss(avg_discount, 10)))
    list_price = selling_price / (1 - discount_pct / 100)
    return round(list_price / 100) * 100 - 1, round(discount_pct)


def generate_rating(brand_profile):
    """Generate product rating from brand profile distribution."""
    rating = random.gauss(brand_profile["rating_mean"], brand_profile["rating_std"])
    rating = max(2.5, min(5.0, rating))
    return round(rating * 2) / 2  # Round to nearest 0.5


def generate_review_count(brand_profile):
    """Generate review count from brand range."""
    low, high = brand_profile["review_count_range"]
    # Log-normal distribution to get realistic spread
    log_mean = (math.log(low) + math.log(high)) / 2
    log_std = (math.log(high) - math.log(low)) / 4
    count = int(math.exp(random.gauss(log_mean, log_std)))
    return max(low, min(high, count))


def generate_review_text(brand_profile, rating):
    """Generate a realistic review based on brand profile and rating."""
    if rating >= 4.0:
        template = random.choice(POSITIVE_REVIEW_TEMPLATES)
        strength = random.choice(brand_profile["strengths"])
        strength = strength[0].upper() + strength[1:]
        detail = random.choice(DETAIL_FRAGMENTS)
        aspect = random.choice(ASPECTS)
        aspect_detail_list = ASPECT_POSITIVE_DETAILS.get(random.choice(list(ASPECT_POSITIVE_DETAILS.keys())), ["Quality is good"])
        aspect_detail = random.choice(aspect_detail_list)

        text = template.format(
            product_type=random.choice(["suitcase", "trolley bag", "luggage", "travel bag"]),
            strength=strength,
            detail=detail,
            aspect=aspect,
            months=random.randint(3, 18),
            count=random.randint(2, 5),
            trip_type=random.choice(TRIP_TYPES),
        )
        # Sometimes append an aspect detail
        if random.random() > 0.4:
            text += " " + aspect_detail + "."
        return text

    elif rating <= 2.5:
        template = random.choice(NEGATIVE_REVIEW_TEMPLATES)
        weakness = random.choice(brand_profile["weaknesses"])
        weakness = weakness[0].upper() + weakness[1:]
        detail = random.choice(DETAIL_FRAGMENTS[:5])  # Use neutral details
        aspect = random.choice(ASPECTS)
        aspect_detail_list = ASPECT_NEGATIVE_DETAILS.get(random.choice(list(ASPECT_NEGATIVE_DETAILS.keys())), ["Quality is poor"])
        aspect_detail = random.choice(aspect_detail_list)

        text = template.format(
            weakness=weakness,
            detail=detail,
            aspect=aspect,
            months=random.randint(1, 6),
            count=random.randint(1, 3),
            defect=random.choice(["damaged", "defective", "scratched", "dented"]),
        )
        if random.random() > 0.4:
            text += " " + aspect_detail + "."
        return text

    else:
        template = random.choice(MIXED_REVIEW_TEMPLATES)
        strength = random.choice(brand_profile["strengths"])
        strength = strength[0].upper() + strength[1:]
        weakness = random.choice(brand_profile["weaknesses"])
        detail = random.choice(DETAIL_FRAGMENTS)
        aspect_good = random.choice(["design", "size", "weight", "color"])
        aspect_bad = random.choice(["wheels", "zipper", "handle", "durability"])

        text = template.format(
            strength=strength,
            weakness=weakness,
            detail=detail,
            aspect_good=aspect_good,
            aspect_bad=aspect_bad,
        )
        return text


def generate_review_title(rating):
    """Generate a short review title."""
    if rating >= 4.5:
        return random.choice(["Excellent product!", "Highly recommended", "Best luggage I've owned",
                              "Amazing quality", "Perfect for travel", "Worth every penny", "Love it!",
                              "Super happy with purchase", "Outstanding!", "Five stars deserved"])
    elif rating >= 3.5:
        return random.choice(["Good product", "Nice luggage", "Decent quality", "Happy with purchase",
                              "Good value", "Pretty good", "Satisfactory", "Does the job well",
                              "Recommended", "Good buy"])
    elif rating >= 2.5:
        return random.choice(["Average product", "It's okay", "Could be better", "Mixed feelings",
                              "Decent but has issues", "Not great not terrible", "Fair quality",
                              "Mediocre", "Expected more", "Just about okay"])
    else:
        return random.choice(["Disappointed", "Not worth it", "Poor quality", "Very bad",
                              "Waste of money", "Don't buy", "Terrible quality", "Regret buying",
                              "Below expectations", "Awful"])


def generate_rating_for_review(product_rating):
    """Generate individual review rating clustered around product rating."""
    # Most reviews cluster around the product rating, with some variance
    if random.random() < 0.3:
        # 30% chance of extreme rating
        return random.choice([1, 2, 5, 5, 5])  # Skewed toward 5
    else:
        # 70% chance of rating near product average
        r = random.gauss(product_rating, 0.8)
        r = max(1, min(5, round(r)))
        return int(r)


def generate_review_date():
    """Generate a random review date within the last 2 years."""
    days_ago = random.randint(1, 730)
    date = datetime.now() - timedelta(days=days_ago)
    return date.strftime("%Y-%m-%d")


def main():
    """Generate the complete dataset."""
    os.makedirs("../dataset", exist_ok=True)

    all_products = []
    all_reviews = []
    product_id = 1
    review_id = 1

    for brand_name, profile in BRAND_PROFILES.items():
        print(f"Generating data for {brand_name}...")

        for product_name, category, size_cm in profile["product_lines"]:
            # Generate product data
            selling_price = generate_price(profile, category)
            list_price, discount_pct = generate_list_price(selling_price, profile["avg_discount_pct"])
            rating = generate_rating(profile)
            review_count = generate_review_count(profile)

            product = {
                "id": product_id,
                "brand": brand_name,
                "title": product_name,
                "category": category,
                "size_cm": size_cm,
                "selling_price": selling_price,
                "list_price": list_price,
                "discount_pct": discount_pct,
                "rating": rating,
                "total_reviews": review_count,
                "url": f"https://www.amazon.in/dp/B0{random.randint(10000000, 99999999)}",
            }
            all_products.append(product)

            # Generate reviews (sample 5-8 reviews per product to hit 60+ per brand)
            num_reviews = random.randint(5, 8)
            for _ in range(num_reviews):
                review_rating = generate_rating_for_review(rating)
                review_text = generate_review_text(profile, review_rating)
                review_title = generate_review_title(review_rating)

                review = {
                    "id": review_id,
                    "product_id": product_id,
                    "brand": brand_name,
                    "product_title": product_name,
                    "reviewer_name": f"Amazon Customer",
                    "rating": review_rating,
                    "title": review_title,
                    "text": review_text,
                    "date": generate_review_date(),
                    "verified_purchase": random.random() < 0.85,
                }
                all_reviews.append(review)
                review_id += 1

            product_id += 1

    # Sort reviews by date
    all_reviews.sort(key=lambda x: x["date"], reverse=True)

    # Save datasets
    with open("../dataset/products.json", "w", encoding="utf-8") as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)

    with open("../dataset/reviews.json", "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Dataset generated successfully!")
    print(f"   Products: {len(all_products)} ({len(BRAND_PROFILES)} brands)")
    print(f"   Reviews:  {len(all_reviews)}")
    print(f"   Output:   ../dataset/products.json, ../dataset/reviews.json")


if __name__ == "__main__":
    main()
