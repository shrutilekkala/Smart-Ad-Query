import React, { FormEvent, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

type Result = {
  answer: string;
  intent: string;
  rows: Array<Record<string, string | number>>;
  confidence: string;
  limitations: string[];
};

function App() {
  const [question, setQuestion] = useState("Compare performance by channel");
  const [result, setResult] = useState<Result | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      if (!response.ok) throw new Error("The analytics service returned an error.");
      setResult(await response.json());
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  }

  const columns = result?.rows[0] ? Object.keys(result.rows[0]) : [];

  return (
    <main>
      <header>
        <p className="eyebrow">SEMANTIC CAMPAIGN ANALYTICS</p>
        <h1>Ask the campaign data.</h1>
        <p className="lede">Grounded answers from structured performance data and campaign metadata.</p>
      </header>

      <form onSubmit={submit}>
        <label htmlFor="question">Analyst question</label>
        <div className="query-row">
          <input id="question" value={question} onChange={(event) => setQuestion(event.target.value)} />
          <button disabled={loading}>{loading ? "Analyzing..." : "Run query"}</button>
        </div>
        <div className="examples">
          {[
            "Show the top campaigns",
            "Compare performance by channel",
            "Show underperforming campaigns",
          ].map((example) => (
            <button type="button" className="chip" key={example} onClick={() => setQuestion(example)}>
              {example}
            </button>
          ))}
        </div>
      </form>

      {error && <p className="error">{error}</p>}
      {result && (
        <section className="result">
          <div className="result-heading">
            <div><p className="eyebrow">ANSWER</p><h2>{result.answer}</h2></div>
            <span>{result.confidence} confidence</span>
          </div>
          {result.rows.length > 0 && (
            <div className="table-wrap">
              <table>
                <thead><tr>{columns.map((column) => <th key={column}>{column.replaceAll("_", " ")}</th>)}</tr></thead>
                <tbody>{result.rows.map((row, index) => <tr key={index}>{columns.map((column) => <td key={column}>{row[column]}</td>)}</tr>)}</tbody>
              </table>
            </div>
          )}
          <p className="footnote">Intent: {result.intent}. {result.limitations.join(" ")}</p>
        </section>
      )}
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);

