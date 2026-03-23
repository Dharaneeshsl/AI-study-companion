"use client";

import { useState } from "react";
import QuizCard from "../../components/QuizCard";
import Spinner from "../../components/Spinner";
import {
  generateQuiz,
  submitQuiz,
  QuizQuestion,
  QuizResult,
  QuizAnswer,
} from "../../lib/api";

const USER_ID = "student_001";
const SUBJECTS = ["Maths", "Physics", "Chemistry", "CS", "English"] as const;

export default function QuizPage() {
  const [subject, setSubject] = useState<string>(SUBJECTS[0]);
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [result, setResult] = useState<QuizResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await generateQuiz({ user_id: USER_ID, subject });
      setQuestions(response.questions);
      setAnswers({});
    } catch (err) {
      setError("Unable to generate quiz right now.");
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (id: string, option: string) => {
    setAnswers((prev) => ({ ...prev, [id]: option }));
  };

  const handleSubmit = async () => {
    if (questions.length === 0) return;
    setLoading(true);
    setError(null);
    try {
      const payloadAnswers: QuizAnswer[] = questions.map((q) => ({
        id: q.id,
        selected: answers[q.id] ?? "",
        correct: q.answer,
        question: q.question,
        explanation: q.explanation,
        topic: q.topic,
      }));
      const response = await submitQuiz({ user_id: USER_ID, subject, answers: payloadAnswers });
      setResult(response);
    } catch (err) {
      setError("Unable to submit quiz right now.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="space-y-5">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold">Personalized Quiz</h1>
        <p className="text-gray-400">Target weak topics pulled from your memory.</p>
      </header>

      <div className="flex flex-wrap items-center gap-3">
        <select
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          className="bg-gray-900 border border-gray-800 rounded-lg px-3 py-2"
        >
          {SUBJECTS.map((subj) => (
            <option key={subj} value={subj}>
              {subj}
            </option>
          ))}
        </select>
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg"
        >
          Generate Quiz
        </button>
        {loading && <Spinner />}
      </div>

      {error && <p className="text-sm text-red-400">{error}</p>}

      <div className="space-y-4">
        {questions.map((q) => (
          <QuizCard
            key={q.id}
            question={q}
            selected={answers[q.id] ?? ""}
            onSelect={handleSelect}
          />
        ))}
      </div>

      {questions.length > 0 && (
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg"
        >
          Submit Answers
        </button>
      )}

      {result && (
        <div className="bg-gray-900/60 border border-gray-800 rounded-2xl p-4 space-y-2">
          <h2 className="text-xl font-semibold">Your Score</h2>
          <p className="text-2xl text-emerald-400">
            {result.score} / {result.total}
          </p>
          <div className="space-y-2">
            {result.feedback.map((fb) => (
              <div key={fb.id} className="text-sm text-gray-300">
                <p className={fb.correct ? "text-emerald-400" : "text-red-400"}>
                  {fb.correct ? "Correct" : "Incorrect"} — {fb.topic}
                </p>
                {!fb.correct && (
                  <p className="text-gray-400">Correct: {fb.correct_answer} | {fb.explanation}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
