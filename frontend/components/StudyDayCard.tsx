import { StudyDay } from "../lib/api";

interface StudyDayCardProps {
  day: StudyDay;
}

export default function StudyDayCard({ day }: StudyDayCardProps) {
  return (
    <div className="bg-gray-900/70 border border-gray-800 rounded-2xl p-4 space-y-3">
      <h3 className="text-lg font-semibold">{day.day}</h3>
      <div className="space-y-3">
        {day.sessions.map((session, idx) => (
          <div key={`${day.day}-${idx}`} className="bg-gray-950/70 border border-gray-800 rounded-xl p-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-purple-300">{session.subject}</span>
              <span className="text-xs text-gray-400">{session.time}</span>
            </div>
            <p className="text-sm text-gray-300 mt-1">{session.focus}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
