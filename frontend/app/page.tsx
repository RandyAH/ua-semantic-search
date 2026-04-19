"use client";

import { useState } from "react";

type Result = {
  name: string;
  description: string;
  url: string;
  score: number;
};

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ??
  "https://backend-922244788351.us-central1.run.app";

function Spinner({ className }: { className?: string }) {
  return (
    <span
      className={`inline-block size-5 rounded-full border-2 border-neutral-500 border-t-red-400 animate-spin ${className ?? ""}`}
      aria-hidden
    />
  );
}

export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Result[]>([]);
  const [recent, setRecent] = useState<string[]>([]);
  const [visited, setVisited] = useState<Result[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearchWithQuery = async (q: string) => {
    if (!q.trim()) return;

    setLoading(true);

    try {
      const res = await fetch(`${API_BASE.replace(/\/$/, "")}/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: q }),
      });

      const data = await res.json();
      setResults(data.results || []);
      setRecent((prev) => [q, ...prev.filter((x) => x !== q).slice(0, 9)]);
      setHasSearched(true);
    } catch (err) {
      console.error("Error:", err);
    }

    setLoading(false);
  };

  const handleSearch = () => handleSearchWithQuery(query);

  return (
    <div className="flex h-screen min-h-0 overflow-hidden bg-neutral-900 text-neutral-100 antialiased">
      {/* Sidebar */}
      <aside className="flex h-full min-h-0 w-72 shrink-0 flex-col border-r border-neutral-800/80 bg-neutral-950/50 backdrop-blur-sm">
        <div className="shrink-0 border-b border-neutral-800/80 px-5 py-5">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-neutral-500">
            History
          </p>
          <h2 className="mt-1 text-sm font-semibold text-neutral-200">
            Recent searches
          </h2>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto px-3 py-4">
          <div className="space-y-1">
            {recent.length === 0 ? (
              <p className="px-2 py-3 text-sm text-neutral-500">
                Your searches appear here
              </p>
            ) : (
              recent.map((r, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => {
                    setQuery(r);
                    handleSearchWithQuery(r);
                  }}
                  className="w-full rounded-lg px-3 py-2.5 text-left text-sm text-neutral-300 transition-colors duration-200 hover:bg-neutral-800/80 hover:text-white"
                >
                  <span className="line-clamp-2 break-words">{r}</span>
                </button>
              ))
            )}
          </div>
        </div>

        <div className="shrink-0 border-t border-neutral-800/80 px-5 py-4">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-neutral-500">
            Links
          </p>
          <h2 className="mt-1 text-sm font-semibold text-neutral-200">
            Recently opened
          </h2>
        </div>
        <div className="min-h-0 flex-1 overflow-y-auto px-3 pb-5">
          <div className="space-y-1">
            {visited.length === 0 ? (
              <p className="px-2 py-3 text-sm text-neutral-500">
                Opened resources appear here
              </p>
            ) : (
              visited.map((v, i) => (
                <a
                  key={i}
                  href={v.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block rounded-lg px-3 py-2.5 text-sm text-neutral-300 transition-colors duration-200 hover:bg-neutral-800/80 hover:text-white"
                >
                  <span className="line-clamp-2 break-words">{v.name}</span>
                </a>
              ))
            )}
          </div>
        </div>
      </aside>

      {/* Main */}
      <main className="flex min-h-0 flex-1 overflow-y-auto">
        <div className="mx-auto flex w-full max-w-2xl flex-col justify-start px-6 pb-12 pt-12 sm:px-10 sm:pt-16">
          <div className="mb-8 text-center sm:mb-10">
            <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-[2.5rem]">
              UA AI Assistant
            </h1>
            <p className="mt-3 text-sm text-neutral-400">
              Search campus resources in natural language
            </p>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row sm:items-stretch sm:gap-3">
            <div className="relative flex-1">
              <input
                className="w-full rounded-2xl border border-neutral-700/80 bg-neutral-800/60 px-5 py-4 text-base text-white shadow-lg shadow-black/20 outline-none ring-offset-2 ring-offset-neutral-900 transition-shadow duration-200 placeholder:text-neutral-500 focus:border-neutral-600 focus:ring-2 focus:ring-red-500/60"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder='Try: "how do I check my grades"'
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                aria-label="Search query"
              />
            </div>
            <button
              type="button"
              onClick={handleSearch}
              className="shrink-0 rounded-2xl bg-red-900/85 px-8 py-4 text-sm font-semibold text-red-50 shadow-md shadow-red-950/30 transition duration-200 hover:bg-red-800 hover:shadow-lg hover:shadow-red-950/40 active:scale-[0.98]"
            >
              Search
            </button>
          </div>

          <div className="mt-8 flex w-full flex-col items-stretch">
            {loading && (
              <div className="flex items-center justify-center gap-3 py-4 text-neutral-400">
                <Spinner />
                <span className="text-sm">Searching…</span>
              </div>
            )}

            {!loading && hasSearched && results.length === 0 && (
              <p className="py-6 text-center text-sm text-neutral-500">
                No matching resources found. Try a different phrase.
              </p>
            )}

            {!loading && results.length > 0 && (
              <div className="w-full space-y-5">
                {/* Best match */}
                <div className="group relative overflow-hidden rounded-2xl border border-red-900/40 bg-neutral-800/70 p-6 shadow-lg shadow-black/25 transition-shadow duration-300 hover:shadow-xl hover:shadow-black/30">
                  <div className="absolute left-0 top-0 h-full w-1 bg-gradient-to-b from-red-500/90 to-red-800/80" />
                  <div className="pl-4">
                    <span className="inline-flex items-center rounded-full bg-red-950/60 px-3 py-1 text-xs font-medium text-red-200 ring-1 ring-red-800/50">
                      Best match
                    </span>
                    <h2 className="mt-4 text-xl font-semibold text-white">
                      {results[0].name}
                    </h2>
                    <p className="mt-2 text-sm leading-relaxed text-neutral-300">
                      {results[0].description}
                    </p>
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
                      className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-red-400 transition hover:text-red-300"
                    >
                      Open resource
                      <span aria-hidden>→</span>
                    </a>
                  </div>
                </div>

                {/* Other results */}
                <div className="space-y-3">
                  {results.slice(1).map((r, i) => (
                    <div
                      key={i}
                      className="group rounded-2xl border border-neutral-700/60 bg-neutral-800/50 p-6 shadow-md shadow-black/15 transition-shadow duration-300 hover:border-neutral-600 hover:shadow-lg"
                    >
                      <h3 className="font-semibold text-neutral-100">{r.name}</h3>
                      <p className="mt-2 text-sm leading-relaxed text-neutral-300">
                        {r.description}
                      </p>
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
                        className="mt-3 inline-flex text-sm font-medium text-red-400/90 transition hover:text-red-300"
                      >
                        Open resource →
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
