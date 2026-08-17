import { SearchResult } from "../api";

interface Props {
  results: SearchResult[];
}

export default function ResultsList({ results }: Props) {
  if (results.length === 0) return null;

  return (
    <ul className="results-list">
      {results.map((r) => (
        <li key={r.ad.id} className="result-card">
          <div className="result-header">
            <span className="campaign">{r.ad.campaign_name}</span>
            <span className="platform">{r.ad.platform}</span>
            <span className="score">match {(r.score * 100).toFixed(0)}%</span>
          </div>
          <p className="ad-copy">{r.ad.ad_copy}</p>
          <div className="metrics">
            <span>CTR {(r.ad.ctr * 100).toFixed(2)}%</span>
            <span>CPC ${r.ad.cpc.toFixed(2)}</span>
            <span>ROAS {r.ad.roas.toFixed(2)}x</span>
            <span>Spend ${r.ad.spend.toLocaleString()}</span>
            <span>Revenue ${r.ad.revenue.toLocaleString()}</span>
          </div>
        </li>
      ))}
    </ul>
  );
}
