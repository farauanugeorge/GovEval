import { VerdictResponse } from "@/lib/api";
import VerdictBadge from "@/components/VerdictBadge";
import CopyButton from "@/components/CopyButton";
import { Metadata } from "next";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchVerdict(slug: string): Promise<VerdictResponse> {
  const res = await fetch(`${API_BASE}/api/verdict/${slug}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Verdict not found");
  return res.json();
}

export async function generateMetadata({
  params,
}: {
  params: { slug: string };
}): Promise<Metadata> {
  try {
    const verdict = await fetchVerdict(params.slug);
    const label = verdict.verdict.toUpperCase();
    return {
      title: `${verdict.slug} - Verdict: ${label}`,
      description: verdict.summary.slice(0, 160),
      openGraph: {
        title: `Policy Verdict: ${label}`,
        description: verdict.summary.slice(0, 160),
      },
    };
  } catch {
    return { title: "Verdict not found" };
  }
}

export default async function VerdictPage({
  params,
}: {
  params: { slug: string };
}) {
  let verdict: VerdictResponse;
  try {
    verdict = await fetchVerdict(params.slug);
  } catch {
    return (
      <div className="text-center py-16">
        <h1 className="text-2xl font-bold">Verdict not found</h1>
        <p className="text-gray-500 mt-2">
          This verdict may not exist or is still being generated.
        </p>
        <a
          href="/"
          className="inline-block mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg"
        >
          Go home
        </a>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Header */}
      <div className="space-y-4">
        <div className="flex items-center gap-4">
          <VerdictBadge verdict={verdict.verdict} size="lg" />
          <div>
            <span className="text-sm text-gray-500">
              Confidence: {verdict.confidence}%
            </span>
            <span className="text-sm text-gray-400 ml-3">
              {verdict.studies_used} studies analyzed
            </span>
          </div>
        </div>
        <p className="text-xs text-gray-400">
          {new Date(verdict.created_at).toLocaleDateString("en-US", {
            year: "numeric",
            month: "long",
            day: "numeric",
          })}
        </p>
      </div>

      {/* Summary */}
      <section>
        <h2 className="text-xl font-bold mb-3">Summary</h2>
        <p className="text-gray-700 leading-relaxed">{verdict.summary}</p>
      </section>

      {/* Evidence For */}
      {verdict.evidence_for.length > 0 && (
        <section>
          <h2 className="text-xl font-bold mb-3 text-green-800">
            Evidence supporting this policy
          </h2>
          <ul className="space-y-3">
            {verdict.evidence_for.map((e, i) => (
              <li
                key={i}
                className="p-3 bg-green-50 border border-green-200 rounded-lg"
              >
                <p className="text-sm text-gray-800">{e.claim}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {e.title}
                  {e.doi && (
                    <>
                      {" "}
                      &middot;{" "}
                      <a
                        href={`https://doi.org/${e.doi}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        DOI
                      </a>
                    </>
                  )}
                </p>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Evidence Against */}
      {verdict.evidence_against.length > 0 && (
        <section>
          <h2 className="text-xl font-bold mb-3 text-red-800">
            Evidence against this policy
          </h2>
          <ul className="space-y-3">
            {verdict.evidence_against.map((e, i) => (
              <li
                key={i}
                className="p-3 bg-red-50 border border-red-200 rounded-lg"
              >
                <p className="text-sm text-gray-800">{e.claim}</p>
                <p className="text-xs text-gray-500 mt-1">
                  {e.title}
                  {e.doi && (
                    <>
                      {" "}
                      &middot;{" "}
                      <a
                        href={`https://doi.org/${e.doi}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        DOI
                      </a>
                    </>
                  )}
                </p>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Policy text */}
      <section>
        <h2 className="text-xl font-bold mb-3">Original policy text</h2>
        <div className="p-4 bg-gray-100 rounded-lg text-sm text-gray-700 whitespace-pre-wrap max-h-64 overflow-y-auto">
          {verdict.policy_text}
        </div>
      </section>

      {/* Disclaimer */}
      <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
        <strong>Disclaimer:</strong> This is an automated analysis based on
        peer-reviewed academic abstracts. It is not legal, academic, or policy
        advice. The verdict reflects what the retrieved literature suggests, not
        a definitive assessment. Always consult domain experts for
        decision-making.
      </div>

      {/* Share + CTA */}
      <div className="flex gap-4">
        <CopyButton slug={verdict.slug} />
        <a
          href="/"
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
        >
          Submit a similar policy
        </a>
      </div>
    </div>
  );
}
