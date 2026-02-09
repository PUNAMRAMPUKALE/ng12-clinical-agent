import type { Citation } from "../api";

export default function CitationList({ citations }: { citations: Citation[] }) {
  if (!citations || citations.length === 0) {
    return (
      <div className="rounded-lg border border-slate-800 bg-slate-950/50 p-3 text-sm text-slate-400">
        No citations returned.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {citations.map((c, idx) => (
        <div
          key={`${c.chunk_id}-${idx}`}
          className="rounded-xl border border-slate-800 bg-slate-950/40 p-4"
        >
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="rounded-full bg-slate-800 px-2 py-1 text-slate-200">
              {c.source || "NG12 PDF"}
            </span>
            <span className="rounded-full bg-indigo-500/15 px-2 py-1 text-indigo-200">
              p.{c.page}
            </span>
            <span className="rounded-full bg-cyan-500/15 px-2 py-1 text-cyan-200">
              {c.chunk_id}
            </span>
          </div>

          {c.excerpt ? (
            <p className="mt-3 whitespace-pre-wrap text-sm text-slate-200">
              {c.excerpt}
            </p>
          ) : (
            <p className="mt-3 text-sm text-slate-400">(No excerpt)</p>
          )}
        </div>
      ))}
    </div>
  );
}
