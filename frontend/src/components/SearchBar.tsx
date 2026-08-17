import { FormEvent, useState } from "react";

interface Props {
  onSearch: (query: string) => void;
  onAsk: (question: string) => void;
  loading: boolean;
}

export default function SearchBar({ onSearch, onAsk, loading }: Props) {
  const [value, setValue] = useState("");

  const submit = (e: FormEvent, mode: "search" | "ask") => {
    e.preventDefault();
    if (!value.trim()) return;
    if (mode === "search") onSearch(value.trim());
    else onAsk(value.trim());
  };

  return (
    <form className="search-bar">
      <input
        type="text"
        placeholder='Try: "eco-friendly car buyers" or "which campaign has the best ROAS?"'
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
      <button onClick={(e) => submit(e, "search")} disabled={loading}>
        Search
      </button>
      <button onClick={(e) => submit(e, "ask")} disabled={loading} className="ask-btn">
        Ask (RAG)
      </button>
    </form>
  );
}
