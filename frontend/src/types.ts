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
  citations: Citation[];
  confidence?: number | null;
  retrieval_debug?: Record<string, unknown>;
};

export type ChatResponse = {
  session_id: string;
  answer: string;
  citations: Citation[];
};

export type ChatTurn = {
  role: "user" | "assistant";
  content: string;
  citations: Citation[];
};

export type ChatHistoryResponse = {
  session_id: string;
  history: ChatTurn[];
};
