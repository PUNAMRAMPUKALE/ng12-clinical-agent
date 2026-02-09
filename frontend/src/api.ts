const API_BASE =
  import.meta.env.VITE_API_BASE?.toString().trim() || "http://127.0.0.1:8000";

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export type Citation = {
  source?: string;
  page: number;
  chunk_id: string;
  excerpt?: string;
};

export type AssessResponse = {
  patient_id: string;
  assessment: string;
  reasoning: string;
  confidence?: number | null;
  citations: Citation[];
  retrieval_debug?: Record<string, any>;
};

export type ChatResponse = {
  session_id: string;
  answer: string;
  citations: Citation[];
};

export type ChatHistoryTurn = {
  role: "user" | "assistant";
  content: string;
  citations: Citation[];
};

export type ChatHistoryResponse = {
  session_id: string;
  history: ChatHistoryTurn[];
};

export async function assess(patient_id: string, top_k: number): Promise<AssessResponse> {
  return http<AssessResponse>("/assess", {
    method: "POST",
    body: JSON.stringify({ patient_id, top_k }),
  });
}

export async function chat(session_id: string, message: string, top_k: number): Promise<ChatResponse> {
  return http<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify({ session_id, message, top_k }),
  });
}

export async function chatHistory(session_id: string): Promise<ChatHistoryResponse> {
  return http<ChatHistoryResponse>(`/chat/${encodeURIComponent(session_id)}/history`);
}

export async function clearChat(session_id: string): Promise<{ session_id: string; cleared: boolean }> {
  return http(`/chat/${encodeURIComponent(session_id)}`, { method: "DELETE" });
}
