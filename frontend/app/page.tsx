"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import ChatBubble from "../components/ChatBubble";
import { sendChat, ChatMessage } from "../lib/api";
import Spinner from "../components/Spinner";
import { getUserIdFromToken } from "../lib/auth";

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    const id = getUserIdFromToken();
    setUserId(id);
    if (!id) router.push("/login");
  }, [router]);

  const handleSend = async () => {
    if (!input.trim()) return;
    if (!userId) {
      setError("Please log in to continue.");
      return;
    }
    const userMessage: ChatMessage = { role: "user", content: input.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);
    setError(null);
    try {
      const reply = await sendChat({ message: userMessage.content });
      const assistantMessage: ChatMessage = { role: "assistant", content: reply.reply };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="space-y-4">
      <header className="space-y-2">
        <h1 className="text-3xl font-semibold">Chat Tutor</h1>
        <p className="text-gray-400">Ask questions, get guidance, and build your memory-driven study streak.</p>
      </header>

      <div className="bg-gray-900/60 border border-gray-800 rounded-2xl p-4 min-h-[320px]">
        {messages.length === 0 ? (
          <p className="text-gray-500">Start by asking a question about any topic you are studying.</p>
        ) : (
          <div className="space-y-3">
            {messages.map((msg, idx) => (
              <ChatBubble key={`${msg.role}-${idx}`} role={msg.role} content={msg.content} />
            ))}
          </div>
        )}
      </div>

      <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-4 space-y-2">
        <textarea
          className="w-full bg-gray-950 border border-gray-800 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          rows={3}
          placeholder="Type your question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
        <div className="flex items-center justify-between">
          <button
            onClick={handleSend}
            disabled={loading}
            className="bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white px-4 py-2 rounded-lg"
          >
            Send
          </button>
          {loading && <Spinner />}
        </div>
        {error && <p className="text-sm text-red-400">{error}</p>}
      </div>
    </section>
  );
}
