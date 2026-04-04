"use client";

import { useEffect, useState } from "react";
import { getVerdicts, VerdictListItem } from "@/lib/api";
import VerdictBadge from "@/components/VerdictBadge";

export default function VerdictsArchive() {
  const [verdicts, setVerdicts] = useState<VerdictListItem[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const pageSize = 20;

  useEffect(() => {
    setLoading(true);
    getVerdicts(page, pageSize)
      .then((data) => {
        setVerdicts(data.items);
        setTotal(data.total);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page]);

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Verdict archive</h1>
      <p className="text-gray-600">
        All policy verdicts are public and permanently accessible.
      </p>

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : verdicts.length === 0 ? (
        <p className="text-gray-500">No verdicts yet.</p>
      ) : (
        <>
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
                <p className="text-sm text-gray-700 line-clamp-2">
                  {v.summary}
                </p>
              </a>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex justify-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 border rounded text-sm disabled:opacity-50"
              >
                Previous
              </button>
              <span className="px-3 py-1 text-sm text-gray-600">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-1 border rounded text-sm disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
