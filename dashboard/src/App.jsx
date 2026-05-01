import { useState, useEffect } from 'react';
import './index.css';
import OverviewPage from './pages/OverviewPage';
import ComparisonPage from './pages/ComparisonPage';
import DrilldownPage from './pages/DrilldownPage';

const TABS = [
  { id: 'overview', label: '📊 Overview' },
  { id: 'comparison', label: '⚔️ Brand Comparison' },
  { id: 'drilldown', label: '🔍 Product Drilldown' },
];

export default function App() {
  const [tab, setTab] = useState('overview');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    brands: [],
    minPrice: 0,
    maxPrice: 20000,
    minRating: 0,
    category: 'all',
    sentiment: 'all',
  });

  useEffect(() => {
    Promise.all([
      fetch('/data/products.json').then(r => r.json()),
      fetch('/data/reviews.json').then(r => r.json()),
      fetch('/data/brand_summary.json').then(r => r.json()),
      fetch('/data/agent_insights.json').then(r => r.json()),
    ]).then(([products, reviews, brandSummary, insights]) => {
      const allBrands = [...new Set(products.map(p => p.brand))];
      setFilters(f => ({ ...f, brands: allBrands }));
      setData({ products, reviews, brandSummary, insights, allBrands });
      setLoading(false);
    });
  }, []);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner" />
        <p style={{ color: 'var(--text-secondary)' }}>Loading dashboard data...</p>
      </div>
    );
  }

  const filtered = applyFilters(data, filters);

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-inner">
          <div className="logo">
            <div className="logo-icon">CI</div>
            <div className="logo-text"><span>LuggageIQ</span> Dashboard</div>
          </div>
          <nav className="nav-tabs">
            {TABS.map(t => (
              <button key={t.id} className={`nav-tab ${tab === t.id ? 'active' : ''}`}
                onClick={() => setTab(t.id)}>{t.label}</button>
            ))}
          </nav>
        </div>
      </header>
      <main className="main-content">
        <FilterBar filters={filters} setFilters={setFilters} allBrands={data.allBrands} />
        {tab === 'overview' && <OverviewPage data={filtered} raw={data} filters={filters} />}
        {tab === 'comparison' && <ComparisonPage data={filtered} raw={data} filters={filters} />}
        {tab === 'drilldown' && <DrilldownPage data={filtered} raw={data} filters={filters} />}
      </main>
    </div>
  );
}

function FilterBar({ filters, setFilters, allBrands }) {
  const update = (key, val) => setFilters(f => ({ ...f, [key]: val }));

  const toggleBrand = (brand) => {
    setFilters(f => {
      const brands = f.brands.includes(brand) ? f.brands.filter(b => b !== brand) : [...f.brands, brand];
      return { ...f, brands };
    });
  };

  return (
    <div className="filter-bar">
      <div className="filter-group">
        <span className="filter-label">Brands</span>
        <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
          {allBrands.map(b => (
            <button key={b} onClick={() => toggleBrand(b)}
              style={{
                padding: '4px 10px', borderRadius: '6px', border: '1px solid',
                borderColor: filters.brands.includes(b) ? 'var(--accent-cyan)' : 'var(--border)',
                background: filters.brands.includes(b) ? 'rgba(34,211,238,0.1)' : 'transparent',
                color: filters.brands.includes(b) ? 'var(--accent-cyan)' : 'var(--text-muted)',
                fontSize: '0.78rem', fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit',
                transition: 'var(--transition)',
              }}>{b}</button>
          ))}
        </div>
      </div>
      <div className="filter-group">
        <span className="filter-label">Min Rating</span>
        <select className="filter-select" value={filters.minRating} onChange={e => update('minRating', +e.target.value)}>
          <option value={0}>All</option>
          <option value={3}>3+ ★</option>
          <option value={3.5}>3.5+ ★</option>
          <option value={4}>4+ ★</option>
          <option value={4.5}>4.5+ ★</option>
        </select>
      </div>
      <div className="filter-group">
        <span className="filter-label">Category</span>
        <select className="filter-select" value={filters.category} onChange={e => update('category', e.target.value)}>
          <option value="all">All Sizes</option>
          <option value="cabin">Cabin</option>
          <option value="medium">Medium</option>
          <option value="large">Large</option>
          <option value="set">Set</option>
        </select>
      </div>
      <div className="filter-group">
        <span className="filter-label">Sentiment</span>
        <select className="filter-select" value={filters.sentiment} onChange={e => update('sentiment', e.target.value)}>
          <option value="all">All</option>
          <option value="positive">Positive</option>
          <option value="neutral">Neutral</option>
          <option value="negative">Negative</option>
        </select>
      </div>
      <div className="filter-group">
        <span className="filter-label">Max Price</span>
        <input type="range" min="1000" max="20000" step="500" value={filters.maxPrice}
          onChange={e => update('maxPrice', +e.target.value)}
          style={{ width: '120px', accentColor: 'var(--accent-cyan)' }} />
        <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>₹{filters.maxPrice.toLocaleString('en-IN')}</span>
      </div>
    </div>
  );
}

function applyFilters(data, filters) {
  let products = data.products.filter(p => {
    if (!filters.brands.includes(p.brand)) return false;
    if (p.selling_price > filters.maxPrice) return false;
    if (p.rating < filters.minRating) return false;
    if (filters.category !== 'all' && p.category !== filters.category) return false;
    return true;
  });

  const productIds = new Set(products.map(p => p.id));

  let reviews = data.reviews.filter(r => {
    if (!productIds.has(r.product_id)) return false;
    if (filters.sentiment !== 'all' && r.sentiment_label !== filters.sentiment) return false;
    return true;
  });

  // Build filtered brand summary
  const brandSummary = {};
  for (const brand of filters.brands) {
    if (data.brandSummary[brand]) {
      brandSummary[brand] = data.brandSummary[brand];
    }
  }

  return { products, reviews, brandSummary, insights: data.insights, allBrands: data.allBrands };
}
