"use client";

import { useState } from "react";
import Spinner from "../../components/Spinner";
import StudyDayCard from "../../components/StudyDayCard";
import { getStudyPlan, StudyPlanResponse } from "../../lib/api";

const USER_ID = "student_001";

export default function StudyPlanPage() {
  const [plan, setPlan] = useState<StudyPlanResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getStudyPlan({ user_id: USER_ID });
      setPlan(response);
    } catch (err) {
      setError("Unable to fetch study plan.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="space-y-5">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold">Weekly Study Plan</h1>
        <p className="text-gray-400">Your plan is built from your memory and upcoming goals.</p>
      </header>

      <button
        onClick={handleGenerate}
        disabled={loading}
        className="bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg"
      >
        Generate My Study Plan
      </button>
      {loading && <Spinner />}
      {error && <p className="text-sm text-red-400">{error}</p>}

      {plan && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {plan.plan.map((day) => (
            <StudyDayCard key={day.day} day={day} />
          ))}
        </div>
      )}
    </section>
  );
}
