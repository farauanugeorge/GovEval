"use client";

import { useEffect, useState } from "react";
import { getVerdicts, VerdictListItem } from "@/lib/api";
import VerdictBadge from "./VerdictBadge";

export default function RecentVerdicts() {
  const [verdicts, setVerdicts] = useState<VerdictListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getVerdicts(1, 10)
      .then((data) => setVerdicts(data.items))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="text-gray-500 text-sm">Loading recent verdicts...</p>;
  }

  if (verdicts.length === 0) {
    return (
      <p className="text-gray-500 text-sm">
        No verdicts yet. Be the first to submit a policy for analysis.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      {verdicts.map((v) => (
        <a
          key={v.slug}
          href={`/verdict/${v.slug}`}
          className="block p-4 bg-white border border-gray-200 rounded-lg hover:border-gray-300 transition"
        >
          <div className="flex items-center justify-between mb-2">
            <VerdictBadge
              verdict={v.verdict as "smart" | "mixed" | "poor"}
              size="sm"
            />
            <span className="text-xs text-gray-500">
              {new Date(v.created_at).toLocaleDateString()} &middot;{" "}
              {v.studies_used} studies &middot; {v.confidence}% confidence
            </span>
          </div>
          <p className="text-sm text-gray-700 line-clamp-2">{v.summary}</p>
        </a>
      ))}
    </div>
  );
}
