import type { ChatMessage } from "../lib/api";

interface ChatBubbleProps {
  role: ChatMessage["role"];
  content: string;
}

export default function ChatBubble({ role, content }: ChatBubbleProps) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm leading-relaxed ${
          isUser
            ? "bg-purple-600 text-white rounded-br-none"
            : "bg-gray-800 text-gray-100 rounded-bl-none"
        }`}
      >
        {content}
      </div>
    </div>
  );
}
