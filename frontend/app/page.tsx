"use client";

import { useState } from "react";

type Result = {
  name: string;
  description: string;
  url: string;
  score: number;
};

export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Result[]>([]);
  const [recent, setRecent] = useState<string[]>([]);
  const [visited, setVisited] = useState<Result[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearchWithQuery = async (q: string) => {
    if (!q.trim()) return;

    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: q }),
      });

      const data = await res.json();
      setResults(data.results || []);
      setRecent((prev) => [q, ...prev.filter((x) => x !== q).slice(0, 9)]);
    } catch (err) {
      console.error("Error:", err);
    }

    setLoading(false);
  };

  const handleSearch = () => handleSearchWithQuery(query);

  return (
    <div className="flex h-screen bg-neutral-800 text-white">
      {/* SIDEBAR */}
      <div className="w-72 bg-neutral-700 p-5 border-r border-neutral-800 flex flex-col">
        {/* RECENT SEARCHES */}
        <div>
          <h2 className="text-lg font-bold mb-4">Recent Searches</h2>

          <div className="space-y-3">
            {recent.map((r, i) => (
              <button
                key={i}
                onClick={() => {
                  setQuery(r);
                  handleSearchWithQuery(r);
                }}
                className="block w-full text-left text-sm text-gray-300 hover:text-white transition rounded-md px-2 py-2 hover:bg-neutral-600 whitespace-normal break-words"
              >
                {r}
              </button>
            ))}
          </div>
        </div>

        {/* BIG SPACING BETWEEN SECTIONS */}
        <div className="my-8 border-t border-neutral-600" />

        {/* RECENTLY OPENED */}
        <div>
          <h2 className="text-lg font-bold mb-4">Recently Opened</h2>

          <div className="space-y-3">
            {visited.map((v, i) => (
              <a
                key={i}
                href={v.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block w-full text-sm text-gray-300 hover:text-white transition rounded-md px-2 py-2 hover:bg-neutral-600 whitespace-normal break-words"
              >
                {v.name}
              </a>
            ))}
          </div>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="flex-1 flex flex-col items-center justify-start p-10">
        <h1 className="text-3xl font-bold mb-6">UA AI Assistant 🔍</h1>

        {/* SEARCH BAR */}
        <div className="w-full max-w-2xl flex gap-2">
          <input
            className="flex-1 p-4 rounded-xl bg-neutral-600 text-white border border-neutral-700 focus:outline-none text-lg"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Try: 'how do I check my grades'"
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />

          <button
            onClick={handleSearch}
            className="bg-red-800 px-6 rounded-xl hover:bg-red-900 transition"
          >
            Search
          </button>
        </div>

        {/* LOADING */}
        {loading && <p className="mt-4 text-neutral-400">Searching...</p>}

        {/* RESULTS */}
        {results.length > 0 && (
          <div className="w-full max-w-2xl mt-8">
            {/* BEST RESULT */}
            <div className="bg-neutral-700 p-6 rounded-2xl border border-red-700 shadow-lg">
              <p className="text-sm text-red-500 font-semibold">🔥 Best Match</p>
              <h2 className="text-xl font-bold mt-2">{results[0].name}</h2>
              <p className="text-neutral-400 mt-1">{results[0].description}</p>

              <a
                href={results[0].url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={() => {
                  setVisited((prev) => [
                    results[0],
                    ...prev.filter((v) => v.url !== results[0].url).slice(0, 5),
                  ]);
                }}
                className="text-red-500 mt-3 inline-block font-semibold hover:underline"
              >
                Open →
              </a>
            </div>

            {/* OTHER RESULTS */}
            <div className="mt-6 space-y-4">
              {results.slice(1).map((r, i) => (
                <div
                  key={i}
                  className="bg-neutral-700 p-5 rounded-xl border border-neutral-800 hover:border-neutral-600 transition"
                >
                  <h2 className="font-semibold">{r.name}</h2>
                  <p className="text-neutral-400">{r.description}</p>

                  <a
                    href={r.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={() => {
                      setVisited((prev) => [
                        r,
                        ...prev.filter((v) => v.url !== r.url).slice(0, 5),
                      ]);
                    }}
                    className="text-red-500 mt-2 inline-block text-sm hover:underline"
                  >
                    Open →
                  </a>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}