export interface ChatRequest {
  user_id: string;
  message: string;
}

export interface ChatResponse {
  reply: string;
}

export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  role: ChatRole;
  content: string;
}

export interface QuizRequest {
  user_id: string;
  subject: string;
}

export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  answer: string;
  explanation: string;
  topic: string;
}

export interface QuizResponse {
  questions: QuizQuestion[];
}

export interface QuizAnswer {
  id: string;
  selected: string;
  correct: string;
  question: string;
  explanation: string;
  topic: string;
}

export interface QuizSubmitRequest {
  user_id: string;
  subject: string;
  answers: QuizAnswer[];
}

export interface QuizFeedback {
  id: string;
  correct: boolean;
  selected: string;
  correct_answer: string;
  explanation: string;
  topic: string;
}

export interface QuizResult {
  score: number;
  total: number;
  feedback: QuizFeedback[];
}

export interface StudyPlanRequest {
  user_id: string;
}

export interface StudySession {
  subject: string;
  time: string;
  focus: string;
}

export interface StudyDay {
  day: string;
  sessions: StudySession[];
}

export interface StudyPlanResponse {
  plan: StudyDay[];
}

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function sendChat(payload: ChatRequest): Promise<ChatResponse> {
  try {
    const response = await fetch(`${BASE_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return await handleResponse<ChatResponse>(response);
  } catch (error) {
    throw error instanceof Error ? error : new Error("Chat failed");
  }
}

export async function generateQuiz(payload: QuizRequest): Promise<QuizResponse> {
  try {
    const response = await fetch(`${BASE_URL}/api/quiz/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return await handleResponse<QuizResponse>(response);
  } catch (error) {
    throw error instanceof Error ? error : new Error("Quiz generation failed");
  }
}

export async function submitQuiz(payload: QuizSubmitRequest): Promise<QuizResult> {
  try {
    const response = await fetch(`${BASE_URL}/api/quiz/submit`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return await handleResponse<QuizResult>(response);
  } catch (error) {
    throw error instanceof Error ? error : new Error("Quiz submit failed");
  }
}

export async function getStudyPlan(payload: StudyPlanRequest): Promise<StudyPlanResponse> {
  try {
    const response = await fetch(`${BASE_URL}/api/study-plan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return await handleResponse<StudyPlanResponse>(response);
  } catch (error) {
    throw error instanceof Error ? error : new Error("Study plan failed");
  }
}
