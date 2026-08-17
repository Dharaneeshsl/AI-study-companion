export interface ChatRequest {
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

export type StudyPlanRequest = Record<string, never>;

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

import { getToken } from "./auth";

function getAuthHeaders() {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const text = await response.text();
    let errorMsg = text;
    try {
        const json = JSON.parse(text);
        if (json.detail) {
            errorMsg = typeof json.detail === "string" ? json.detail : JSON.stringify(json.detail);
        }
    } catch (e) {}
    throw new Error(errorMsg || `Request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function login(payload: any) {
  const formData = new URLSearchParams();
  formData.append("username", payload.username);
  formData.append("password", payload.password);
  
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData.toString()
  });
  return await handleResponse<{access_token: string}>(response);
}

export async function signup(payload: any) {
  const response = await fetch(`${BASE_URL}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  return await handleResponse<any>(response);
}

export async function sendChat(payload: ChatRequest): Promise<ChatResponse> {
  try {
    const response = await fetch(`${BASE_URL}/api/chat`, {
      method: "POST",
      headers: getAuthHeaders(),
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
      headers: getAuthHeaders(),
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
      headers: getAuthHeaders(),
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
      headers: getAuthHeaders(),
      body: JSON.stringify(payload),
    });
    return await handleResponse<StudyPlanResponse>(response);
  } catch (error) {
    throw error instanceof Error ? error : new Error("Study plan failed");
  }
}
