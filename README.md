# LuggageIQ — Competitive Intelligence Dashboard

> **Amazon India Luggage Brand Analysis** | Scrape · Analyze · Compare · Present

A full-stack competitive intelligence dashboard that collects, analyzes, and visualizes customer reviews and pricing data for luggage brands on Amazon India.

![Dashboard Overview](docs/overview.png)

---

## 🎯 What This Dashboard Answers

| Question | Where to Find It |
|----------|-----------------|
| Which brands are priced premium vs value? | Overview → Price Chart, Comparison → Table |
| Which brands rely on heavy discounting? | Overview → Discount Chart, Comparison → Table |
| What do customers praise or complain about? | Comparison → Pros & Cons, Drilldown → Modal |
| Which brands win on sentiment vs price? | Overview → Brand Health Matrix (Bubble Chart) |
| What are the non-obvious insights? | Overview → Agent Insights section |

---

## 📊 Brands Covered

| Brand | Positioning | Products | Reviews |
|-------|------------|----------|---------|
| Safari | Mass-market | 12 | 79 |
| Skybags | Mass-market | 12 | 79 |
| American Tourister | Mid-range | 12 | 80 |
| VIP | Mass-market | 12 | 78 |
| Aristocrat | Budget | 12 | 80 |
| Nasher Miles | Premium-value | 12 | 78 |

**Total: 6 brands, 72 products, 474 reviews analyzed**

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│              Data Pipeline (Python)               │
│                                                    │
│  scraper.py ──► generate_dataset.py ──► analyzer.py│
│  (Playwright)    (Fallback data)      (VADER+NLP) │
│                                                    │
│  Output: dataset/products.json                     │
│          dataset/reviews.json                      │
│          dataset/brand_summary.json                │
│          dataset/agent_insights.json               │
└──────────────────────┬───────────────────────────┘
                       │ JSON files
                       ▼
┌──────────────────────────────────────────────────┐
│            Dashboard (React + Vite)               │
│                                                    │
│  Overview ─── Brand Comparison ─── Product Drilldown│
│  KPIs          Sortable Table       Product Cards   │
│  Bar Charts    Radar Chart          Detail Modal    │
│  Bubble Chart  Aspect Heatmap       Review Analysis │
│  Pie Chart     Pros & Cons          Aspect Sentiment│
│  Agent Insights                     Review Highlights│
└──────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Scraping | Python + Playwright | Browser automation for Amazon India |
| Analysis | VADER Sentiment + Custom NLP | Sentiment scoring, theme extraction |
| Frontend | React 19 + Vite 8 | Fast, modern SPA framework |
| Charts | Recharts | Declarative, composable visualizations |
| Animations | Framer Motion | Smooth micro-interactions |
| Icons | Lucide React | Consistent icon system |
| Styling | Vanilla CSS | Full design control, dark theme |

---

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ and npm
- **Python** 3.10+ (for data pipeline only)

### 1. Install & Run Dashboard
```bash
cd dashboard
npm install
npm run dev
```
Open http://localhost:5173 in your browser.

### 2. (Optional) Regenerate Dataset
```bash
cd scraper
pip install -r requirements.txt

# Generate realistic dataset
python generate_dataset.py

# Run sentiment analysis
python analyzer.py

# Copy to dashboard
cp ../dataset/* ../dashboard/public/data/
```

### 3. (Optional) Scrape Live Data from Amazon India
```bash
cd scraper
pip install playwright
python -m playwright install chromium
python scraper.py    # Scrapes products + reviews
python analyzer.py   # Analyzes scraped data
cp ../dataset/* ../dashboard/public/data/
```

> **Note:** Amazon actively blocks automated scrapers. The scraper includes stealth techniques but may be rate-limited. The `generate_dataset.py` produces realistic data as a reliable fallback.

---

## 📐 Sentiment Methodology

### VADER (Valence Aware Dictionary and sEntiment Reasoner)

We use VADER, a lexicon and rule-based sentiment analysis tool specifically designed for social media and user-generated content. VADER excels at:
- Understanding sentiment intensity ("great" vs "GREAT!!!")
- Handling negations ("not good")
- Processing emoji and slang
- No training data required — works out of the box

### Scoring

| Metric | Range | Meaning |
|--------|-------|---------|
| Compound Score | -1.0 to +1.0 | Overall sentiment polarity |
| Positive (≥ 0.05) | — | Review expresses satisfaction |
| Neutral (-0.05 to 0.05) | — | Review is factual/mixed |
| Negative (≤ -0.05) | — | Review expresses dissatisfaction |

### Aspect-Level Analysis

Custom keyword dictionaries detect mentions of 8 product aspects:

| Aspect | Keywords (sample) |
|--------|------------------|
| Wheels | wheel, spinner, rolling, caster, glide |
| Handle | handle, telescopic, grip, retract |
| Material | polycarbonate, hard shell, build quality, ABS |
| Zipper | zipper, zip, slider, teeth |
| Durability | durable, broke, crack, sturdy, flimsy |
| Size | spacious, compact, cabin, expandable |
| Value | worth, value for money, overpriced, affordable |
| Design | design, look, color, style, aesthetic |

Each aspect gets its own sentiment score, enabling questions like "Which brand has the best wheel sentiment?"

### Value-for-Money Score

```
VFM Score = Brand Sentiment / (Brand Avg Price / Market Avg Price)
```

Higher VFM = more customer satisfaction per rupee spent.

---

## 🎨 Dashboard Views

### 1. Overview
- **6 KPI Cards**: Brands, products, reviews, sentiment, price, rating
- **Price Bar Chart**: Average selling price by brand
- **Sentiment Bar Chart**: VADER compound score by brand
- **Discount Chart**: Average discount percentage
- **Sentiment Pie**: Positive/neutral/negative distribution
- **Brand Health Bubble**: Price vs Sentiment scatter (bubble = review volume)
- **Agent Insights**: 4-7 non-obvious AI-generated conclusions

### 2. Brand Comparison
- **Benchmarking Table**: Sortable by any metric
- **Radar Chart**: 6-axis competitive positioning
- **Aspect Heatmap**: Color-coded sentiment grid (8 aspects × 6 brands)
- **Pros & Cons**: Top 5 themes per brand with frequency bars

### 3. Product Drilldown
- **Product Cards**: Sortable by price, rating, discount, sentiment
- **Detail Modal**: Full product analysis on click
- **Aspect Bars**: Per-product aspect-level sentiment
- **Review Highlights**: Top 10 reviews with sentiment badges
- **Anomaly Badges**: Flags products with high rating but negative sentiment

### Filters (Global)
- Brand selector (multi-toggle)
- Minimum rating filter
- Category (cabin/medium/large/set)
- Sentiment (positive/neutral/negative)
- Max price slider

---

## 📁 Dataset Schema

### products.json
```json
{
  "id": 1,
  "brand": "Safari",
  "title": "Safari Pentagon 55 Cabin Luggage",
  "category": "cabin",
  "size_cm": 55,
  "selling_price": 2299,
  "list_price": 5799,
  "discount_pct": 60,
  "rating": 4.0,
  "total_reviews": 12500,
  "url": "https://www.amazon.in/dp/B0XXXXXXXX"
}
```

### reviews.json (after analysis)
```json
{
  "id": 1,
  "product_id": 1,
  "brand": "Safari",
  "rating": 5,
  "title": "Excellent product!",
  "text": "Very happy with this purchase...",
  "date": "2025-03-15",
  "verified_purchase": true,
  "sentiment_score": 0.927,
  "sentiment_label": "positive",
  "aspects": { "wheels": 0.927, "value": 0.927 },
  "trust_flags": [],
  "is_suspicious": false
}
```

### brand_summary.json
```json
{
  "Safari": {
    "avg_price": 3332,
    "avg_discount_pct": 55.1,
    "avg_rating": 3.67,
    "avg_sentiment": 0.522,
    "vfm_score": 0.701,
    "positioning": "mass-market",
    "aspect_sentiment": { "wheels": { "avg_sentiment": 0.45, "mention_count": 20 } },
    "top_pros": [{ "theme": "good value", "count": 39 }],
    "top_cons": [{ "theme": "poor wheels", "count": 11 }],
    "anomalies": []
  }
}
```

---

## 🏆 Bonus Features Implemented

| Feature | Status | Details |
|---------|--------|---------|
| Aspect-level sentiment | ✅ | 8 aspects tracked per review |
| Anomaly detection | ✅ | Flags high-rating + negative-sentiment mismatches |
| Value-for-money analysis | ✅ | VFM score adjusts sentiment by price band |
| Review trust signals | ✅ | Flags suspicious patterns (short reviews, incentivized) |
| Agent Insights | ✅ | 4-7 non-obvious conclusions from cross-brand analysis |

---

## ⚠️ Limitations & Future Improvements

### Current Limitations
1. **Dataset**: Uses generated data based on real Amazon India patterns. Live scraping is available but may be blocked.
2. **Review Volume**: ~474 analyzed reviews (sampled). Real products have 1K-45K reviews each.
3. **Temporal Analysis**: Limited time-series data for trend detection.
4. **Category Depth**: Size/category detection is heuristic-based.

### Future Improvements
1. **Proxy-based scraping**: Residential proxy rotation for reliable live data
2. **LLM-powered synthesis**: GPT/Claude for deeper review summarization
3. **Time-series tracking**: Monitor price and sentiment trends over weeks
4. **Export functionality**: PDF reports, CSV downloads
5. **Real-time alerts**: Notify when competitor prices change significantly
6. **More brands**: Expand to Samsonite, Tommy Hilfiger, Wildcraft, etc.
7. **Cross-marketplace**: Compare across Flipkart, Myntra, and Amazon

---

## 📄 License

This project is for educational and analytical purposes only. Web scraping should be conducted in compliance with Amazon's Terms of Service and applicable laws.
