"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { submitAnalysis } from "@/lib/api";

export default function SubmitForm() {
  const router = useRouter();
  const [inputType, setInputType] = useState<"text" | "url">("text");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!content.trim()) return;

    setLoading(true);
    setError("");

    try {
      const result = await submitAnalysis(inputType, content);
      router.push(`/analyzing/${result.job_id}?slug=${result.slug}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Submission failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setInputType("text")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
            inputType === "text"
              ? "bg-gray-900 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          Paste text
        </button>
        <button
          type="button"
          onClick={() => setInputType("url")}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
            inputType === "url"
              ? "bg-gray-900 text-white"
              : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          Enter URL
        </button>
      </div>

      {inputType === "text" ? (
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Paste the policy text here..."
          className="w-full h-48 p-4 border border-gray-300 rounded-lg resize-y focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
        />
      ) : (
        <input
          type="url"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="https://example.gov/policy-document"
          className="w-full p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
        />
      )}

      {error && (
        <p className="text-red-600 text-sm">{error}</p>
      )}

      <button
        type="submit"
        disabled={loading || !content.trim()}
        className="w-full py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        {loading ? "Submitting..." : "Analyze Policy"}
      </button>
    </form>
  );
}
