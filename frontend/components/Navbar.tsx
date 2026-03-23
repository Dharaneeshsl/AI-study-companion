"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Chat" },
  { href: "/quiz", label: "Quiz" },
  { href: "/study-plan", label: "Study Plan" },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="border-b border-gray-800 bg-gray-950/80 backdrop-blur">
      <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-8 w-8 rounded-xl bg-purple-600 flex items-center justify-center font-bold">A</div>
          <span className="font-semibold text-lg">AI Study Companion</span>
        </div>
        <div className="flex items-center gap-4 text-sm">
          {links.map((link) => {
            const active = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`px-2 py-1 rounded-lg ${
                  active ? "bg-purple-600 text-white" : "text-gray-300 hover:text-white"
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
