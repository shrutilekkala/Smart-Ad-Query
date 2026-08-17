import { useState } from "react";
import AnalyticsDashboard from "./components/AnalyticsDashboard";
import ResultsList from "./components/ResultsList";
import SearchBar from "./components/SearchBar";
import { RagResponse, SearchResult, api } from "./api";

type Tab = "search" | "analytics";

export default function App() {
  const [tab, setTab] = useState<Tab>("search");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [rag, setRag] = useState<RagResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (query: string) => {
    setLoading(true);
    setError(null);
    setRag(null);
    try {
      const res = await api.search(query, 8);
      setResults(res.results);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAsk = async (question: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.ragQuery(question, 5);
      setRag(res);
      setResults(res.sources);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>SmartAdQuery</h1>
        <p className="subtitle">Semantic search &amp; RAG-powered analytics over ad campaign data</p>
        <nav>
          <button className={tab === "search" ? "active" : ""} onClick={() => setTab("search")}>
            Search
          </button>
          <button className={tab === "analytics" ? "active" : ""} onClick={() => setTab("analytics")}>
            Analytics
          </button>
        </nav>
      </header>

      {tab === "search" && (
        <main>
          <SearchBar onSearch={handleSearch} onAsk={handleAsk} loading={loading} />
          {error && <p className="error">{error}</p>}
          {loading && <p>Loading...</p>}
          {rag && (
            <div className="rag-answer">
              <strong>Answer</strong> <span className="badge">{rag.generated_by}</span>
              <p>{rag.answer}</p>
            </div>
          )}
          <ResultsList results={results} />
        </main>
      )}

      {tab === "analytics" && (
        <main>
          <AnalyticsDashboard />
        </main>
      )}
    </div>
  );
}
