import { useMemo, useState } from "react";
import AssessorPanel from "./components/AssessorPanel";
import ChatPanel from "./components/ChatPanel";

type Tab = "assessor" | "chat";

export default function App() {
  const [tab, setTab] = useState<Tab>("assessor");

  const tabs = useMemo(
    () => [
      { id: "assessor" as const, label: "NG12 Assessor" },
      { id: "chat" as const, label: "Chat (NG12 RAG)" },
    ],
    []
  );

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Background glow */}
      <div className="pointer-events-none fixed inset-0 opacity-60">
        <div className="absolute -top-24 left-1/2 h-64 w-[520px] -translate-x-1/2 rounded-full bg-indigo-600 blur-[120px]" />
        <div className="absolute top-32 left-20 h-56 w-56 rounded-full bg-cyan-500 blur-[120px]" />
        <div className="absolute bottom-10 right-10 h-72 w-72 rounded-full bg-fuchsia-500 blur-[140px]" />
      </div>

      <div className="relative mx-auto max-w-6xl px-4 py-10">
        {/* Header */}
        <div className="flex flex-col gap-2">
          <h1 className="text-2xl font-semibold tracking-tight">
            NG12 Clinical Agent
          </h1>
          <p className="text-sm text-slate-300">
            Decision support + conversational RAG over NICE NG12, grounded with citations.
          </p>
        </div>

        {/* Tabs */}
        <div className="mt-6 inline-flex rounded-xl border border-slate-800 bg-slate-900/60 p-1">
          {tabs.map((t) => {
            const active = tab === t.id;
            return (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={[
                  "rounded-lg px-4 py-2 text-sm transition",
                  active
                    ? "bg-slate-100 text-slate-900"
                    : "text-slate-200 hover:bg-slate-800",
                ].join(" ")}
              >
                {t.label}
              </button>
            );
          })}
        </div>

        {/* Panels */}
        <div className="mt-6">
          {tab === "assessor" ? <AssessorPanel /> : <ChatPanel />}
        </div>

        {/* Footer */}
        <div className="mt-10 border-t border-slate-800 pt-6 text-xs text-slate-400">
          Backend: FastAPI · Vector DB: Chroma · LLM/Embeddings: Vertex AI (Gemini)
        </div>
      </div>
    </div>
  );
}
