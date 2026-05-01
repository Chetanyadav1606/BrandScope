import { useState, useMemo } from 'react';
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
  Cell, Legend,
} from 'recharts';
import { BRAND_COLORS, formatPrice, heatmapColor } from '../utils';

const ASPECTS = ['wheels', 'handle', 'material', 'zipper', 'durability', 'size', 'value', 'design'];

export default function ComparisonPage({ data }) {
  const [sortKey, setSortKey] = useState('avg_sentiment');
  const [sortDir, setSortDir] = useState('desc');

  const brands = useMemo(() => {
    const list = Object.values(data.brandSummary);
    return list.sort((a, b) => sortDir === 'desc' ? (b[sortKey] ?? 0) - (a[sortKey] ?? 0) : (a[sortKey] ?? 0) - (b[sortKey] ?? 0));
  }, [data.brandSummary, sortKey, sortDir]);

  const handleSort = (key) => {
    if (sortKey === key) setSortDir(d => d === 'desc' ? 'asc' : 'desc');
    else { setSortKey(key); setSortDir('desc'); }
  };

  const sortIcon = (key) => sortKey === key ? (sortDir === 'desc' ? ' ▼' : ' ▲') : ' ↕';

  // Radar data
  const radarData = useMemo(() => {
    const metrics = ['Price Competitiveness', 'Sentiment', 'Rating', 'Discount Attractiveness', 'Review Volume', 'Value for Money'];
    const maxPrice = Math.max(...brands.map(b => b.avg_price));
    const maxReviews = Math.max(...brands.map(b => b.review_count));
    const maxVfm = Math.max(...brands.map(b => Math.abs(b.vfm_score)));

    return metrics.map(metric => {
      const entry = { metric };
      brands.forEach(b => {
        let val = 0;
        if (metric === 'Price Competitiveness') val = ((maxPrice - b.avg_price) / maxPrice) * 100;
        else if (metric === 'Sentiment') val = b.avg_sentiment * 100;
        else if (metric === 'Rating') val = (b.avg_rating / 5) * 100;
        else if (metric === 'Discount Attractiveness') val = b.avg_discount_pct;
        else if (metric === 'Review Volume') val = (b.review_count / maxReviews) * 100;
        else if (metric === 'Value for Money') val = maxVfm ? (b.vfm_score / maxVfm) * 100 : 0;
        entry[b.brand] = +Math.max(0, val).toFixed(1);
      });
      return entry;
    });
  }, [brands]);

  // Rating comparison bar data
  const ratingData = brands.map(b => ({
    brand: b.brand, rating: b.avg_rating, fill: BRAND_COLORS[b.brand],
  }));

  return (
    <div className="fade-in">
      <div className="section-header">
        <h1 className="section-title">Brand Comparison</h1>
        <p className="section-subtitle">Side-by-side benchmarking of price, sentiment, rating, and product themes</p>
      </div>

      {/* Comparison Table */}
      <div className="glass-card" style={{ marginBottom: '1.5rem', overflow: 'auto' }}>
        <div className="card-header"><div className="card-title">Brand Benchmarking Table</div></div>
        <div className="card-body">
          <table className="data-table">
            <thead>
              <tr>
                <th>Brand</th>
                <th onClick={() => handleSort('avg_price')} className={sortKey === 'avg_price' ? 'sorted' : ''}>
                  Avg Price<span className="sort-icon">{sortIcon('avg_price')}</span></th>
                <th onClick={() => handleSort('avg_discount_pct')} className={sortKey === 'avg_discount_pct' ? 'sorted' : ''}>
                  Avg Discount<span className="sort-icon">{sortIcon('avg_discount_pct')}</span></th>
                <th onClick={() => handleSort('avg_rating')} className={sortKey === 'avg_rating' ? 'sorted' : ''}>
                  Rating<span className="sort-icon">{sortIcon('avg_rating')}</span></th>
                <th onClick={() => handleSort('review_count')} className={sortKey === 'review_count' ? 'sorted' : ''}>
                  Reviews<span className="sort-icon">{sortIcon('review_count')}</span></th>
                <th onClick={() => handleSort('avg_sentiment')} className={sortKey === 'avg_sentiment' ? 'sorted' : ''}>
                  Sentiment<span className="sort-icon">{sortIcon('avg_sentiment')}</span></th>
                <th onClick={() => handleSort('vfm_score')} className={sortKey === 'vfm_score' ? 'sorted' : ''}>
                  VFM Score<span className="sort-icon">{sortIcon('vfm_score')}</span></th>
                <th>Positioning</th>
              </tr>
            </thead>
            <tbody>
              {brands.map(b => (
                <tr key={b.brand}>
                  <td><span className={`brand-dot ${BRAND_COLORS[b.brand] ? '' : ''}`}
                    style={{ background: BRAND_COLORS[b.brand] }} /><strong>{b.brand}</strong></td>
                  <td>{formatPrice(b.avg_price)}</td>
                  <td>{b.avg_discount_pct}%</td>
                  <td><span className="star">★</span> {b.avg_rating}</td>
                  <td>{b.review_count}</td>
                  <td><span className={`sentiment-badge ${b.avg_sentiment >= 0.05 ? 'sentiment-positive' : b.avg_sentiment <= -0.05 ? 'sentiment-negative' : 'sentiment-neutral'}`}>
                    {(b.avg_sentiment * 100).toFixed(0)}%</span></td>
                  <td style={{ fontWeight: 600, color: b.vfm_score > 0.5 ? 'var(--accent-green)' : 'var(--text-secondary)' }}>
                    {b.vfm_score.toFixed(2)}</td>
                  <td><span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600,
                    background: b.positioning === 'budget' ? 'rgba(34,211,238,0.1)' : b.positioning === 'premium' ? 'rgba(167,139,250,0.1)' : 'rgba(251,146,60,0.1)',
                    color: b.positioning === 'budget' ? 'var(--accent-cyan)' : b.positioning === 'premium' ? 'var(--accent-purple)' : 'var(--accent-orange)',
                  }}>{b.positioning}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Radar + Rating Charts */}
      <div className="charts-grid">
        <div className="glass-card">
          <div className="card-header">
            <div><div className="card-title">Multi-Axis Brand Comparison</div>
            <div className="card-subtitle">Radar view of competitive positioning</div></div>
          </div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={350}>
              <RadarChart data={radarData} margin={{ top: 20, right: 30, bottom: 20, left: 30 }}>
                <PolarGrid stroke="rgba(255,255,255,0.08)" />
                <PolarAngleAxis dataKey="metric" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                {brands.map(b => (
                  <Radar key={b.brand} name={b.brand} dataKey={b.brand}
                    stroke={BRAND_COLORS[b.brand]} fill={BRAND_COLORS[b.brand]}
                    fillOpacity={0.08} strokeWidth={2} />
                ))}
                <Legend wrapperStyle={{ fontSize: '0.78rem' }} />
                <Tooltip contentStyle={{ background: '#0c1425', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '0.82rem' }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card">
          <div className="card-header">
            <div><div className="card-title">Star Rating Comparison</div>
            <div className="card-subtitle">Average product rating per brand</div></div>
          </div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={ratingData} margin={{ left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="brand" stroke="#64748b" fontSize={10} angle={-20} textAnchor="end" height={60} />
                <YAxis domain={[0, 5]} stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ background: '#0c1425', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                <Bar dataKey="rating" radius={[6,6,0,0]} barSize={36}>
                  {ratingData.map((e, i) => <Cell key={i} fill={e.fill} fillOpacity={0.8} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Aspect Sentiment Heatmap */}
      <div className="glass-card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-header">
          <div><div className="card-title">Aspect-Level Sentiment Heatmap</div>
          <div className="card-subtitle">How each brand performs on specific product attributes (green = positive, red = negative)</div></div>
        </div>
        <div className="card-body" style={{ overflowX: 'auto' }}>
          <div className="heatmap-grid" style={{ gridTemplateColumns: `140px repeat(${ASPECTS.length}, 1fr)`, minWidth: '600px' }}>
            <div className="heatmap-label"></div>
            {ASPECTS.map(a => <div key={a} className="heatmap-label" style={{ textTransform: 'capitalize' }}>{a}</div>)}
            {brands.map(b => (
              <>
                <div key={`l-${b.brand}`} className="heatmap-label" style={{ textAlign: 'left', fontWeight: 600, color: BRAND_COLORS[b.brand] }}>{b.brand}</div>
                {ASPECTS.map(a => {
                  const asp = b.aspect_sentiment?.[a];
                  const val = asp?.avg_sentiment ?? 0;
                  const mentions = asp?.mention_count ?? 0;
                  return (
                    <div key={`${b.brand}-${a}`} className="heatmap-cell"
                      style={{ background: heatmapColor(val), color: 'var(--text-primary)' }}
                      title={`${b.brand} - ${a}: ${val.toFixed(3)} (${mentions} mentions)`}>
                      {mentions > 0 ? (val * 100).toFixed(0) + '%' : '—'}
                    </div>
                  );
                })}
              </>
            ))}
          </div>
        </div>
      </div>

      {/* Pros & Cons */}
      <div className="section-header"><h2 className="section-title">Top Pros & Cons by Brand</h2></div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '1rem' }}>
        {brands.map(b => (
          <div key={b.brand} className="glass-card">
            <div className="card-header">
              <div className="card-title" style={{ color: BRAND_COLORS[b.brand] }}>{b.brand}</div>
            </div>
            <div className="card-body">
              <div className="pros-cons">
                <div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-green)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Strengths</div>
                  {(b.top_pros || []).slice(0, 5).map((t, i) => (
                    <div key={i} className="theme-item">
                      <div className="theme-bar theme-bar-pro" style={{ width: `${Math.min(100, t.count * 8)}px` }} />
                      <span>{t.theme}</span>
                      <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>({t.count})</span>
                    </div>
                  ))}
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-red)', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Weaknesses</div>
                  {(b.top_cons || []).slice(0, 5).map((t, i) => (
                    <div key={i} className="theme-item">
                      <div className="theme-bar theme-bar-con" style={{ width: `${Math.min(100, t.count * 8)}px` }} />
                      <span>{t.theme}</span>
                      <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>({t.count})</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
