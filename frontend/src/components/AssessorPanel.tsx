import { useMemo, useState } from "react";
import { assess, type AssessResponse } from "../api";
import CitationList from "./CitationList";

function formatPct(x?: number | null) {
  if (x === null || x === undefined) return "—";
  const v = Math.max(0, Math.min(1, x));
  return `${Math.round(v * 100)}%`;
}

export default function AssessorPanel() {
  const [patientId, setPatientId] = useState("PT-110");
  const [topK, setTopK] = useState(5);

  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [result, setResult] = useState<AssessResponse | null>(null);

  const badge = useMemo(() => {
    const a = (result?.assessment || "").toLowerCase();
    if (a.includes("urgent")) return "bg-amber-500/15 text-amber-200 border-amber-500/20";
    if (a.includes("unclear")) return "bg-slate-500/15 text-slate-200 border-slate-500/20";
    return "bg-emerald-500/15 text-emerald-200 border-emerald-500/20";
  }, [result?.assessment]);

  async function onAssess() {
    setErr(null);
    setLoading(true);
    setResult(null);
    try {
      const res = await assess(patientId.trim(), Number(topK));
      setResult(res);
    } catch (e: any) {
      setErr(e?.message || "Assessment failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="grid gap-5 lg:grid-cols-3">
      {/* Left: Form */}
      <div className="lg:col-span-1">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg shadow-black/30">
          <div className="text-sm font-medium text-slate-200">Run NG12 Assessment</div>
          <p className="mt-1 text-xs text-slate-400">
            Enter a Patient ID from <code className="text-slate-200">patients.json</code>
          </p>

          <div className="mt-4 space-y-3">
            <div>
              <label className="text-xs text-slate-300">Patient ID</label>
              <input
                value={patientId}
                onChange={(e) => setPatientId(e.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm outline-none focus:border-indigo-400"
                placeholder="PT-110"
              />
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
              onClick={onAssess}
              disabled={loading}
              className={[
                "mt-2 w-full rounded-xl px-4 py-2 text-sm font-medium transition",
                loading
                  ? "bg-slate-700 text-slate-300"
                  : "bg-indigo-500 text-white hover:bg-indigo-400",
              ].join(" ")}
            >
              {loading ? "Assessing..." : "Assess"}
            </button>

            {err && (
              <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-3 text-sm text-red-200">
                {err}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Right: Result */}
      <div className="lg:col-span-2 space-y-5">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg shadow-black/30">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="text-sm font-medium text-slate-200">Result</div>
              <div className="mt-1 text-xs text-slate-400">
                Shows the agent assessment + citations from NG12 chunks.
              </div>
            </div>

            {result && (
              <div className="flex items-center gap-2">
                <span className={`rounded-full border px-3 py-1 text-xs ${badge}`}>
                  {result.assessment}
                </span>
                <span className="rounded-full border border-slate-800 bg-slate-950/40 px-3 py-1 text-xs text-slate-200">
                  Confidence: {formatPct(result.confidence ?? null)}
                </span>
              </div>
            )}
          </div>

          {!result ? (
            <div className="mt-6 rounded-xl border border-slate-800 bg-slate-950/40 p-6 text-sm text-slate-400">
              Run an assessment to see output here.
            </div>
          ) : (
            <>
              <div className="mt-5 rounded-xl border border-slate-800 bg-slate-950/40 p-4">
                <div className="text-xs text-slate-400">Reasoning</div>
                <div className="mt-2 whitespace-pre-wrap text-sm text-slate-100">
                  {result.reasoning}
                </div>
              </div>

              {result.retrieval_debug && (
                <details className="mt-4 rounded-xl border border-slate-800 bg-slate-950/30 p-4">
                  <summary className="cursor-pointer text-sm text-slate-200">
                    Retrieval debug
                  </summary>
                  <pre className="mt-3 overflow-auto text-xs text-slate-300">
                    {JSON.stringify(result.retrieval_debug, null, 2)}
                  </pre>
                </details>
              )}
            </>
          )}
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 shadow-lg shadow-black/30">
          <div className="text-sm font-medium text-slate-200">Citations</div>
          <div className="mt-1 text-xs text-slate-400">
            Page + chunk_id + excerpt pulled from the vector store.
          </div>

          <div className="mt-4">
            <CitationList citations={result?.citations || []} />
          </div>
        </div>
      </div>
    </div>
  );
}
