import { QuizQuestion } from "../lib/api";

interface QuizCardProps {
  question: QuizQuestion;
  selected: string;
  onSelect: (id: string, option: string) => void;
}

export default function QuizCard({ question, selected, onSelect }: QuizCardProps) {
  return (
    <div className="bg-gray-900/70 border border-gray-800 rounded-2xl p-4 space-y-3">
      <div className="space-y-1">
        <p className="text-sm text-purple-300 uppercase tracking-wide">{question.topic}</p>
        <h3 className="text-lg font-semibold">{question.question}</h3>
      </div>
      <div className="space-y-2">
        {question.options.map((option) => (
          <label
            key={option}
            className={`flex items-center gap-2 border rounded-lg px-3 py-2 cursor-pointer ${
              selected === option ? "border-purple-500 bg-purple-500/10" : "border-gray-800"
            }`}
          >
            <input
              type="radio"
              name={question.id}
              value={option}
              checked={selected === option}
              onChange={() => onSelect(question.id, option)}
              className="accent-purple-500"
            />
            <span>{option}</span>
          </label>
        ))}
      </div>
    </div>
  );
}
