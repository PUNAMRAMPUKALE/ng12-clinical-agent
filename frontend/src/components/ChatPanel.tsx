import { useEffect, useMemo, useState } from "react";
import { chat, chatHistory, clearChat, type ChatHistoryTurn, type Citation } from "../api";
import CitationList from "./CitationList";

function newSessionId() {
  return `sess-${Math.random().toString(16).slice(2, 10)}`;
}

export default function ChatPanel() {
  const [sessionId, setSessionId] = useState<string>(() => "e2e-1");
  const [topK, setTopK] = useState<number>(5);
  const [message, setMessage] = useState<string>("");

  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const [turns, setTurns] = useState<ChatHistoryTurn[]>([]);
  const [lastCitations, setLastCitations] = useState<Citation[]>([]);

  const canSend = useMemo(() => {
    return sessionId.trim().length > 0 && message.trim().length > 0 && !loading;
  }, [sessionId, message, loading]);

  async function loadHistory() {
    setErr(null);
    try {
      const h = await chatHistory(sessionId.trim());
      setTurns(h.history || []);
      // pick last assistant citations
      const lastAssist = [...(h.history || [])].reverse().find((t) => t.role === "assistant");
      setLastCitations(lastAssist?.citations || []);
    } catch (e: any) {
      setTurns([]);
      setLastCitations([]);
      setErr(e?.message || "Failed to load history.");
    }
  }

  async function onClear() {
    setErr(null);
    try {
      await clearChat(sessionId.trim());
      setTurns([]);
      setLastCitations([]);
    } catch (e: any) {
      setErr(e?.message || "Failed to clear chat.");
    }
  }

  async function onSend() {
    const sid = sessionId.trim();
    const msg = message.trim();
    if (!sid || !msg) return;

    setErr(null);
    setLoading(true);

    // optimistic append user message
    setTurns((prev) => [...prev, { role: "user", content: msg, citations: [] }]);
    setMessage("");

    try {
      const res = await chat(sid, msg, Number(topK));
      setTurns((prev) => [
        ...prev,
        { role: "assistant", content: res.answer, citations: res.citations || [] },
      ]);
      setLastCitations(res.citations || []);
    } catch (e: any) {
      setErr(e?.message || "Chat failed.");
      // add assistant error bubble
      setTurns((prev) => [
        ...prev,
        { role: "assistant", content: "Error: could not generate answer.", citations: [] },
      ]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    // auto-load on first mount for convenience
    loadHistory();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="grid gap-5 lg:grid-cols-3">
      {/* Left: controls */}
      <div className="lg:col-span-1">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg shadow-black/30">
          <div className="text-sm font-medium text-slate-200">Chat Settings</div>

          <div className="mt-4 space-y-3">
            <div>
              <label className="text-xs text-slate-300">Session ID</label>
              <input
                value={sessionId}
                onChange={(e) => setSessionId(e.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm outline-none focus:border-indigo-400"
                placeholder="e.g. abc123"
              />
              <div className="mt-2 flex gap-2">
                <button
                  onClick={() => setSessionId(newSessionId())}
                  className="rounded-xl border border-slate-800 bg-slate-950/50 px-3 py-2 text-xs text-slate-200 hover:bg-slate-800"
                >
                  New session
                </button>
                <button
                  onClick={loadHistory}
                  className="rounded-xl border border-slate-800 bg-slate-950/50 px-3 py-2 text-xs text-slate-200 hover:bg-slate-800"
                >
                  Load history
                </button>
              </div>
            </div>

            <div>
              <label className="text-xs text-slate-300">Top-K</label>
              <input
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                type="number"
                min={1}
                max={20}
                className="mt-1 w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm outline-none focus:border-indigo-400"
              />
            </div>

            <button
              onClick={onClear}
              className="w-full rounded-xl border border-slate-800 bg-slate-950/50 px-4 py-2 text-sm text-slate-200 hover:bg-slate-800"
            >
              Clear session
            </button>

            {err && (
              <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-200">
                {err}
              </div>
            )}
          </div>
        </div>

        <div className="mt-5 rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg shadow-black/30">
          <div className="text-sm font-medium text-slate-200">Latest citations</div>
          <div className="mt-1 text-xs text-slate-400">
            Shown for the most recent assistant answer.
          </div>
          <div className="mt-4">
            <CitationList citations={lastCitations} />
          </div>
        </div>
      </div>

      {/* Right: chat window */}
      <div className="lg:col-span-2">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 shadow-lg shadow-black/30">
          <div className="border-b border-slate-800 px-5 py-4">
            <div className="text-sm font-medium text-slate-200">Conversation</div>
            <div className="mt-1 text-xs text-slate-400">
              Grounded answers with citations. If evidence is missing, the agent should say so.
            </div>
          </div>

          <div className="h-[460px] overflow-auto p-5">
            {turns.length === 0 ? (
              <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-6 text-sm text-slate-400">
                No messages yet. Ask something like:{" "}
                <span className="text-slate-200">
                  “Summarize the referral criteria for visible haematuria.”
                </span>
              </div>
            ) : (
              <div className="space-y-4">
                {turns.map((t, i) => (
                  <div
                    key={i}
                    className={[
                      "max-w-[92%] rounded-2xl border px-4 py-3",
                      t.role === "user"
                        ? "ml-auto border-indigo-500/20 bg-indigo-500/10"
                        : "mr-auto border-slate-800 bg-slate-950/40",
                    ].join(" ")}
                  >
                    <div className="mb-1 text-xs uppercase tracking-wide text-slate-400">
                      {t.role}
                    </div>
                    <div className="whitespace-pre-wrap text-sm text-slate-100">
                      {t.content}
                    </div>

                    {t.role === "assistant" && t.citations && t.citations.length > 0 && (
                      <details className="mt-3">
                        <summary className="cursor-pointer text-xs text-slate-300">
                          Show citations ({t.citations.length})
                        </summary>
                        <div className="mt-3">
                          <CitationList citations={t.citations} />
                        </div>
                      </details>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="border-t border-slate-800 p-4">
            <div className="flex gap-2">
              <input
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    if (canSend) onSend();
                  }
                }}
                placeholder="Ask a question about NG12 (press Enter to send)…"
                className="flex-1 rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm outline-none focus:border-indigo-400"
              />
              <button
                onClick={onSend}
                disabled={!canSend}
                className={[
                  "rounded-xl px-4 py-2 text-sm font-medium transition",
                  canSend
                    ? "bg-indigo-500 text-white hover:bg-indigo-400"
                    : "bg-slate-700 text-slate-300",
                ].join(" ")}
              >
                {loading ? "Sending..." : "Send"}
              </button>
            </div>
            <div className="mt-2 text-xs text-slate-400">
              Tip: follow-ups work better if you reuse the same session.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
