// Brand color mapping
export const BRAND_COLORS = {
  'Safari': '#22d3ee',
  'Skybags': '#a78bfa',
  'American Tourister': '#f472b6',
  'VIP': '#fb923c',
  'Aristocrat': '#34d399',
  'Nasher Miles': '#60a5fa',
};

export const BRAND_CSS = {
  'Safari': 'brand-safari',
  'Skybags': 'brand-skybags',
  'American Tourister': 'brand-american-tourister',
  'VIP': 'brand-vip',
  'Aristocrat': 'brand-aristocrat',
  'Nasher Miles': 'brand-nasher-miles',
};

export const formatPrice = (val) => `₹${Number(val).toLocaleString('en-IN')}`;
export const formatPct = (val) => `${val}%`;
export const formatSentiment = (val) => (val >= 0 ? '+' : '') + val.toFixed(3);

export const getSentimentLabel = (score) => {
  if (score >= 0.05) return 'positive';
  if (score <= -0.05) return 'negative';
  return 'neutral';
};

export const getSentimentClass = (score) => `sentiment-${getSentimentLabel(score)}`;

export const sentimentColor = (val) => {
  if (val >= 0.3) return '#34d399';
  if (val >= 0.05) return '#86efac';
  if (val >= -0.05) return '#fb923c';
  return '#f87171';
};

export const heatmapColor = (val) => {
  if (val >= 0.5) return 'rgba(52,211,153,0.35)';
  if (val >= 0.3) return 'rgba(52,211,153,0.2)';
  if (val >= 0.1) return 'rgba(52,211,153,0.1)';
  if (val >= -0.1) return 'rgba(251,146,60,0.15)';
  if (val >= -0.3) return 'rgba(248,113,113,0.2)';
  return 'rgba(248,113,113,0.35)';
};

export const CHART_THEME = {
  backgroundColor: 'transparent',
  textColor: '#94a3b8',
  gridColor: 'rgba(255,255,255,0.05)',
  tooltipBg: '#0c1425',
};
