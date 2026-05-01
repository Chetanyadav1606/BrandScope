import { useState, useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import { BRAND_COLORS, formatPrice } from '../utils';

export default function DrilldownPage({ data }) {
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [sortKey, setSortKey] = useState('selling_price');
  const [sortDir, setSortDir] = useState('asc');

  const products = useMemo(() => {
    const list = data.products.map(p => {
      const pRevs = data.reviews.filter(r => r.product_id === p.id);
      const avgSent = pRevs.length ? pRevs.reduce((s, r) => s + (r.sentiment_score || 0), 0) / pRevs.length : 0;
      const posCount = pRevs.filter(r => r.sentiment_label === 'positive').length;
      const negCount = pRevs.filter(r => r.sentiment_label === 'negative').length;
      return { ...p, reviewsData: pRevs, avgSentiment: avgSent, posCount, negCount, analyzedReviews: pRevs.length };
    });
    return list.sort((a, b) => sortDir === 'desc' ? (b[sortKey] ?? 0) - (a[sortKey] ?? 0) : (a[sortKey] ?? 0) - (b[sortKey] ?? 0));
  }, [data.products, data.reviews, sortKey, sortDir]);

  return (
    <div className="fade-in">
      <div className="section-header">
        <h1 className="section-title">Product Drilldown</h1>
        <p className="section-subtitle">{products.length} products — click any card for detailed review analysis</p>
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1rem', flexWrap: 'wrap' }}>
        {[
          { key: 'selling_price', label: 'Price' },
          { key: 'rating', label: 'Rating' },
          { key: 'discount_pct', label: 'Discount' },
          { key: 'avgSentiment', label: 'Sentiment' },
        ].map(s => (
          <button key={s.key} onClick={() => { if (sortKey === s.key) setSortDir(d => d === 'desc' ? 'asc' : 'desc'); else { setSortKey(s.key); setSortDir('desc'); } }}
            style={{
              padding: '6px 14px', borderRadius: '8px', fontFamily: 'inherit', fontSize: '0.82rem', fontWeight: 600,
              border: `1px solid ${sortKey === s.key ? 'var(--accent-cyan)' : 'var(--border)'}`,
              background: sortKey === s.key ? 'rgba(34,211,238,0.1)' : 'transparent',
              color: sortKey === s.key ? 'var(--accent-cyan)' : 'var(--text-muted)',
              cursor: 'pointer',
            }}>
            {s.label} {sortKey === s.key ? (sortDir === 'desc' ? '▼' : '▲') : ''}
          </button>
        ))}
      </div>

      <div className="products-grid">
        {products.map(p => (
          <div key={p.id} className="product-card" onClick={() => setSelectedProduct(p)}>
            <div className="product-brand" style={{ color: BRAND_COLORS[p.brand] }}>{p.brand}</div>
            <div className="product-title">{p.title}</div>
            <div className="product-meta">
              <span className="product-price">{formatPrice(p.selling_price)}</span>
              <span className="product-list-price">{formatPrice(p.list_price)}</span>
              <span className="product-discount">-{p.discount_pct}%</span>
            </div>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
              <span className="product-rating"><span className="star">★</span> {p.rating}</span>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>{p.total_reviews.toLocaleString()} reviews</span>
              <span className={`sentiment-badge ${p.avgSentiment >= 0.05 ? 'sentiment-positive' : p.avgSentiment <= -0.05 ? 'sentiment-negative' : 'sentiment-neutral'}`}>
                {(p.avgSentiment * 100).toFixed(0)}%
              </span>
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem', textTransform: 'capitalize' }}>
              {p.category} {p.size_cm ? `• ${p.size_cm}cm` : ''}
            </div>
            {p.rating >= 4.0 && p.avgSentiment < 0 && (
              <div style={{ marginTop: '0.5rem', padding: '4px 8px', borderRadius: '4px', fontSize: '0.72rem', fontWeight: 700, background: 'rgba(248,113,113,0.12)', color: 'var(--accent-red)' }}>
                ⚠️ Anomaly: High rating, negative sentiment
              </div>
            )}
          </div>
        ))}
      </div>

      {selectedProduct && <ProductModal product={selectedProduct} onClose={() => setSelectedProduct(null)} />}
    </div>
  );
}

function ProductModal({ product, onClose }) {
  const p = product;
  const reviews = p.reviewsData || [];

  const sentimentDist = [
    { label: 'Positive', count: p.posCount, color: '#34d399' },
    { label: 'Neutral', count: reviews.filter(r => r.sentiment_label === 'neutral').length, color: '#fb923c' },
    { label: 'Negative', count: p.negCount, color: '#f87171' },
  ];

  // Extract review themes
  const posReviews = reviews.filter(r => r.sentiment_label === 'positive');
  const negReviews = reviews.filter(r => r.sentiment_label === 'negative');

  // Get aspect mentions
  const aspectData = {};
  reviews.forEach(r => {
    Object.entries(r.aspects || {}).forEach(([asp, score]) => {
      if (!aspectData[asp]) aspectData[asp] = { mentions: 0, totalScore: 0 };
      aspectData[asp].mentions++;
      aspectData[asp].totalScore += score;
    });
  });
  const aspectBars = Object.entries(aspectData).map(([asp, d]) => ({
    aspect: asp.charAt(0).toUpperCase() + asp.slice(1),
    sentiment: +((d.totalScore / d.mentions) * 100).toFixed(1),
    mentions: d.mentions,
    fill: d.totalScore / d.mentions >= 0 ? '#34d399' : '#f87171',
  })).sort((a, b) => b.sentiment - a.sentiment);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>

        <div className="product-brand" style={{ color: BRAND_COLORS[p.brand], marginBottom: '0.3rem' }}>{p.brand}</div>
        <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '1rem', paddingRight: '2rem' }}>{p.title}</h2>

        {/* Price & Rating Row */}
        <div style={{ display: 'flex', gap: '2rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.2rem' }}>Selling Price</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--accent-green)' }}>{formatPrice(p.selling_price)}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.2rem' }}>List Price</div>
            <div style={{ fontSize: '1.1rem', color: 'var(--text-muted)', textDecoration: 'line-through' }}>{formatPrice(p.list_price)}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.2rem' }}>Discount</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-orange)' }}>-{p.discount_pct}%</div>
          </div>
          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.2rem' }}>Rating</div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700 }}><span className="star">★</span> {p.rating}</div>
          </div>
          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.2rem' }}>Sentiment</div>
            <span className={`sentiment-badge ${p.avgSentiment >= 0.05 ? 'sentiment-positive' : p.avgSentiment <= -0.05 ? 'sentiment-negative' : 'sentiment-neutral'}`}>
              {(p.avgSentiment * 100).toFixed(0)}%</span>
          </div>
        </div>

        {/* Sentiment Distribution */}
        <h3 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.75rem' }}>Review Sentiment Distribution</h3>
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
          {sentimentDist.map(s => (
            <div key={s.label} style={{ flex: 1, textAlign: 'center', padding: '0.75rem', borderRadius: '10px', background: `${s.color}10`, border: `1px solid ${s.color}30` }}>
              <div style={{ fontSize: '1.3rem', fontWeight: 800, color: s.color }}>{s.count}</div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{s.label}</div>
            </div>
          ))}
        </div>

        {/* Aspect Sentiment */}
        {aspectBars.length > 0 && (
          <>
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.75rem' }}>Aspect-Level Sentiment</h3>
            <div style={{ marginBottom: '1.5rem' }}>
              <ResponsiveContainer width="100%" height={Math.max(160, aspectBars.length * 36)}>
                <BarChart data={aspectBars} layout="vertical" margin={{ left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis type="number" stroke="#64748b" fontSize={10} tickFormatter={v => v + '%'} />
                  <YAxis type="category" dataKey="aspect" stroke="#64748b" fontSize={11} width={80} />
                  <Tooltip contentStyle={{ background: '#0c1425', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                    formatter={(v, n, props) => [`${v}% (${props.payload.mentions} mentions)`, 'Sentiment']} />
                  <Bar dataKey="sentiment" radius={[0, 6, 6, 0]} barSize={18}>
                    {aspectBars.map((e, i) => <Cell key={i} fill={e.fill} fillOpacity={0.7} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </>
        )}

        {/* Sample Reviews */}
        <h3 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.75rem' }}>Review Highlights ({reviews.length} analyzed)</h3>
        <div style={{ display: 'grid', gap: '0.5rem', maxHeight: '300px', overflowY: 'auto' }}>
          {reviews.slice(0, 10).map((r, i) => (
            <div key={i} style={{ padding: '0.75rem 1rem', borderRadius: '8px', background: 'var(--bg-glass)', border: '1px solid var(--border)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem', alignItems: 'center' }}>
                <strong style={{ fontSize: '0.85rem' }}>{r.title}</strong>
                <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                  <span className="star" style={{ fontSize: '0.82rem' }}>{'★'.repeat(r.rating)}{'☆'.repeat(5 - r.rating)}</span>
                  <span className={`sentiment-badge ${r.sentiment_label === 'positive' ? 'sentiment-positive' : r.sentiment_label === 'negative' ? 'sentiment-negative' : 'sentiment-neutral'}`}>
                    {(r.sentiment_score * 100).toFixed(0)}%</span>
                </div>
              </div>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5, margin: 0 }}>{r.text}</p>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>
                {r.date} {r.verified_purchase && '• ✓ Verified'} {r.is_suspicious && '• ⚠ Flagged'}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
