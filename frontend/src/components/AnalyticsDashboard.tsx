import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { AnalyticsSummary, api } from "../api";

export default function AnalyticsDashboard() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .analyticsSummary()
      .then(setSummary)
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">Failed to load analytics: {error}</p>;
  if (!summary) return <p>Loading analytics...</p>;

  const topCampaigns = [...summary.campaigns]
    .sort((a, b) => b.revenue - a.revenue)
    .slice(0, 8);

  return (
    <div className="dashboard">
      <div className="stat-row">
        <div className="stat">
          <span className="stat-label">Total Spend</span>
          <span className="stat-value">${summary.total_spend.toLocaleString()}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Total Revenue</span>
          <span className="stat-value">${summary.total_revenue.toLocaleString()}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Overall CTR</span>
          <span className="stat-value">{(summary.overall_ctr * 100).toFixed(2)}%</span>
        </div>
        <div className="stat">
          <span className="stat-label">Overall ROAS</span>
          <span className="stat-value">{summary.overall_roas.toFixed(2)}x</span>
        </div>
      </div>

      <h3>Top Campaigns by Revenue</h3>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={topCampaigns} margin={{ top: 10, right: 20, left: 0, bottom: 60 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="campaign_name" angle={-30} textAnchor="end" interval={0} height={80} />
          <YAxis />
          <Tooltip />
          <Bar dataKey="revenue" fill="#4f46e5" name="Revenue ($)" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
