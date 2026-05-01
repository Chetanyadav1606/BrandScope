import { useMemo } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ScatterChart, Scatter, ZAxis, Cell, CartesianGrid, Legend, PieChart, Pie,
} from 'recharts';
import { BRAND_COLORS, formatPrice, formatSentiment } from '../utils';

export default function OverviewPage({ data, raw }) {
  const brands = Object.values(data.brandSummary);
  const totalProducts = data.products.length;
  const totalReviews = data.reviews.length;
  const totalListedReviews = brands.reduce((s, b) => s + (b.total_listed_reviews || 0), 0);
  const avgSentiment = brands.length ? brands.reduce((s, b) => s + b.avg_sentiment, 0) / brands.length : 0;
  const avgPrice = brands.length ? brands.reduce((s, b) => s + b.avg_price, 0) / brands.length : 0;
  const avgRating = brands.length ? brands.reduce((s, b) => s + b.avg_rating, 0) / brands.length : 0;

  const priceData = brands.map(b => ({
    brand: b.brand, avg: b.avg_price, min: b.min_price, max: b.max_price,
    fill: BRAND_COLORS[b.brand],
  })).sort((a, b) => a.avg - b.avg);

  const sentimentData = brands.map(b => ({
    brand: b.brand, sentiment: +(b.avg_sentiment * 100).toFixed(1),
    fill: BRAND_COLORS[b.brand],
  })).sort((a, b) => b.sentiment - a.sentiment);

  const discountData = brands.map(b => ({
    brand: b.brand, discount: b.avg_discount_pct,
    fill: BRAND_COLORS[b.brand],
  })).sort((a, b) => b.discount - a.discount);

  const bubbleData = brands.map(b => ({
    brand: b.brand, x: b.avg_price, y: +(b.avg_sentiment * 100).toFixed(1),
    z: b.review_count, rating: b.avg_rating,
    fill: BRAND_COLORS[b.brand],
  }));

  const sentDistData = useMemo(() => {
    const pos = data.reviews.filter(r => r.sentiment_label === 'positive').length;
    const neu = data.reviews.filter(r => r.sentiment_label === 'neutral').length;
    const neg = data.reviews.filter(r => r.sentiment_label === 'negative').length;
    return [
      { name: 'Positive', value: pos, fill: '#34d399' },
      { name: 'Neutral', value: neu, fill: '#fb923c' },
      { name: 'Negative', value: neg, fill: '#f87171' },
    ];
  }, [data.reviews]);

  return (
    <div className="fade-in">
      <div className="section-header">
        <h1 className="section-title">Market Overview</h1>
        <p className="section-subtitle">Competitive intelligence snapshot across {brands.length} luggage brands on Amazon India</p>
      </div>

      {/* KPI Cards */}
      <div className="kpi-grid">
        <KPI label="Brands Tracked" value={brands.length} icon="🏷️" color="var(--accent-cyan)" />
        <KPI label="Products Analyzed" value={totalProducts} icon="📦" color="var(--accent-purple)" />
        <KPI label="Reviews Analyzed" value={totalReviews} icon="💬" color="var(--accent-green)" sub={`${totalListedReviews.toLocaleString()} total listed`} />
        <KPI label="Avg Sentiment" value={`+${(avgSentiment * 100).toFixed(0)}%`} icon="😊" color="var(--accent-orange)" />
        <KPI label="Avg Price" value={formatPrice(avgPrice)} icon="💰" color="var(--accent-blue)" />
        <KPI label="Avg Rating" value={avgRating.toFixed(1) + ' ★'} icon="⭐" color="var(--accent-pink)" />
      </div>

      {/* Charts Row 1 */}
      <div className="charts-grid">
        <div className="glass-card">
          <div className="card-header">
            <div><div className="card-title">Average Selling Price by Brand</div>
            <div className="card-subtitle">Lower = more value-focused positioning</div></div>
          </div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={priceData} layout="vertical" margin={{ left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis type="number" tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} stroke="#64748b" fontSize={11} />
                <YAxis type="category" dataKey="brand" stroke="#64748b" fontSize={11} width={120} />
                <Tooltip formatter={(v) => formatPrice(v)} contentStyle={{ background: '#0c1425', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                <Bar dataKey="avg" radius={[0,6,6,0]} barSize={22}>
                  {priceData.map((e, i) => <Cell key={i} fill={e.fill} fillOpacity={0.8} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card">
          <div className="card-header">
            <div><div className="card-title">Brand Sentiment Score</div>
            <div className="card-subtitle">VADER compound score (higher = more positive)</div></div>
          </div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={sentimentData} layout="vertical" margin={{ left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis type="number" stroke="#64748b" fontSize={11} domain={[0, 100]} tickFormatter={v => v + '%'} />
                <YAxis type="category" dataKey="brand" stroke="#64748b" fontSize={11} width={120} />
                <Tooltip formatter={(v) => v + '%'} contentStyle={{ background: '#0c1425', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                <Bar dataKey="sentiment" radius={[0,6,6,0]} barSize={22}>
                  {sentimentData.map((e, i) => <Cell key={i} fill={e.fill} fillOpacity={0.8} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="charts-grid">
        <div className="glass-card">
          <div className="card-header">
            <div><div className="card-title">Discount Dependency</div>
            <div className="card-subtitle">Higher discounts may signal inflated list prices</div></div>
          </div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={discountData} layout="vertical" margin={{ left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis type="number" stroke="#64748b" fontSize={11} tickFormatter={v => v + '%'} />
                <YAxis type="category" dataKey="brand" stroke="#64748b" fontSize={11} width={120} />
                <Tooltip formatter={(v) => v + '%'} contentStyle={{ background: '#0c1425', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                <Bar dataKey="discount" radius={[0,6,6,0]} barSize={22}>
                  {discountData.map((e, i) => <Cell key={i} fill={e.fill} fillOpacity={0.8} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card">
          <div className="card-header">
            <div><div className="card-title">Sentiment Distribution</div>
            <div className="card-subtitle">Overall review polarity across all brands</div></div>
          </div>
          <div className="card-body" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={sentDistData} cx="50%" cy="50%" innerRadius={60} outerRadius={100}
                  paddingAngle={3} dataKey="value" label={({ name, percent }) => `${name} ${(percent*100).toFixed(0)}%`}
                  fontSize={11} stroke="none">
                  {sentDistData.map((e, i) => <Cell key={i} fill={e.fill} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#0c1425', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Brand Health Bubble */}
      <div className="glass-card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <div><div className="card-title">Brand Health Matrix — Price vs Sentiment</div>
          <div className="card-subtitle">Bubble size = review count. Top-left = best value, bottom-right = premium but lower satisfaction</div></div>
        </div>
        <div className="card-body">
          <ResponsiveContainer width="100%" height={340}>
            <ScatterChart margin={{ top: 20, right: 40, bottom: 20, left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis type="number" dataKey="x" name="Avg Price" tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} stroke="#64748b" fontSize={11} label={{ value: 'Average Price →', position: 'bottom', fill: '#64748b', fontSize: 11 }} />
              <YAxis type="number" dataKey="y" name="Sentiment" stroke="#64748b" fontSize={11} label={{ value: 'Sentiment % →', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 11 }} />
              <ZAxis type="number" dataKey="z" range={[200, 600]} />
              <Tooltip cursor={{ strokeDasharray: '3 3' }}
                content={({ payload }) => {
                  if (!payload?.length) return null;
                  const d = payload[0].payload;
                  return (
                    <div style={{ background: '#0c1425', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', padding: '10px 14px', fontSize: '0.82rem' }}>
                      <div style={{ fontWeight: 700, marginBottom: 4 }}>{d.brand}</div>
                      <div>Price: {formatPrice(d.x)}</div>
                      <div>Sentiment: {d.y}%</div>
                      <div>Reviews: {d.z}</div>
                      <div>Rating: {d.rating} ★</div>
                    </div>
                  );
                }} />
              <Scatter data={bubbleData}>
                {bubbleData.map((e, i) => <Cell key={i} fill={e.fill} fillOpacity={0.75} stroke={e.fill} strokeWidth={2} />)}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Agent Insights */}
      <div className="section-header">
        <h2 className="section-title">🤖 Agent Insights</h2>
        <p className="section-subtitle">Non-obvious conclusions generated from cross-brand analysis</p>
      </div>
      <div className="insights-grid">
        {data.insights.map((ins, i) => (
          <div key={i} className="insight-card">
            <div className="insight-num">Insight #{ins.id || i + 1}</div>
            <div className="insight-title">{ins.title}</div>
            <div className="insight-text">{ins.insight}</div>
            <span className="insight-tag">{ins.category}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function KPI({ label, value, icon, color, sub }) {
  return (
    <div className="kpi-card">
      <div className="kpi-icon" style={{ background: `${color}15`, color }}>{icon}</div>
      <div className="kpi-value" style={{ color }}>{value}</div>
      <div className="kpi-label">{label}</div>
      {sub && <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>{sub}</div>}
    </div>
  );
}
