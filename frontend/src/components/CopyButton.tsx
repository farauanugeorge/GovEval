"use client";

import { useState } from "react";

export default function CopyButton({ slug }: { slug: string }) {
  const [copied, setCopied] = useState(false);

  function handleCopy() {
    navigator.clipboard.writeText(
      `${window.location.origin}/verdict/${slug}`
    );
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <button
      onClick={handleCopy}
      className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
    >
      {copied ? "Copied!" : "Copy share link"}
    </button>
  );
}
