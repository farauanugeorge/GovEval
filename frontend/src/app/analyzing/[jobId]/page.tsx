"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { getAnalysisStatus } from "@/lib/api";

const STEPS = [
  "Reading policy text",
  "Generating search queries",
  "Searching academic databases",
  "Ranking relevant studies",
  "Generating verdict",
];

export default function AnalyzingPage() {
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const jobId = params.jobId as string;

  const [currentStep, setCurrentStep] = useState<string | null>(null);
  const [status, setStatus] = useState("pending");

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const data = await getAnalysisStatus(jobId);
        setStatus(data.status);
        if (data.progress_step) setCurrentStep(data.progress_step);

        if (data.status === "complete" && data.slug) {
          clearInterval(interval);
          router.push(`/verdict/${data.slug}`);
        } else if (data.status === "failed") {
          clearInterval(interval);
        }
      } catch {
        // Keep polling on transient errors
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [jobId, router]);

  function getStepStatus(step: string) {
    const currentIndex = STEPS.indexOf(currentStep || "");
    const stepIndex = STEPS.indexOf(step);
    if (stepIndex < currentIndex) return "done";
    if (stepIndex === currentIndex) return "active";
    return "pending";
  }

  if (status === "failed") {
    return (
      <div className="max-w-lg mx-auto text-center py-16 space-y-4">
        <div className="text-4xl">&#x26A0;</div>
        <h1 className="text-2xl font-bold">Analysis failed</h1>
        <p className="text-gray-600">
          Something went wrong while analyzing this policy. Please try again.
        </p>
        <a
          href="/"
          className="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Try again
        </a>
      </div>
    );
  }

  return (
    <div className="max-w-lg mx-auto py-16">
      <h1 className="text-2xl font-bold text-center mb-2">
        Analyzing policy...
      </h1>
      <p className="text-gray-500 text-center mb-8 text-sm">
        This typically takes 30-90 seconds
      </p>

      <div className="space-y-3">
        {STEPS.map((step) => {
          const s = getStepStatus(step);
          return (
            <div key={step} className="flex items-center gap-3">
              <div
                className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                  s === "done"
                    ? "bg-green-500 text-white"
                    : s === "active"
                    ? "bg-blue-500 text-white animate-pulse"
                    : "bg-gray-200 text-gray-400"
                }`}
              >
                {s === "done" ? "\u2713" : s === "active" ? "\u2026" : ""}
              </div>
              <span
                className={`text-sm ${
                  s === "done"
                    ? "text-green-700"
                    : s === "active"
                    ? "text-blue-700 font-medium"
                    : "text-gray-400"
                }`}
              >
                {step}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
