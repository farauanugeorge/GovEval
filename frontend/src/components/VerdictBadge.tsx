const BADGE_STYLES = {
  smart: "bg-green-100 text-green-800 border-green-300",
  mixed: "bg-amber-100 text-amber-800 border-amber-300",
  poor: "bg-red-100 text-red-800 border-red-300",
} as const;

const LABELS = {
  smart: "SMART",
  mixed: "MIXED",
  poor: "POOR",
} as const;

export default function VerdictBadge({
  verdict,
  size = "md",
}: {
  verdict: "smart" | "mixed" | "poor";
  size?: "sm" | "md" | "lg";
}) {
  const sizeClasses = {
    sm: "px-2 py-0.5 text-xs",
    md: "px-3 py-1 text-sm",
    lg: "px-5 py-2 text-lg",
  };

  return (
    <span
      className={`inline-block font-bold rounded-full border ${BADGE_STYLES[verdict]} ${sizeClasses[size]}`}
    >
      {LABELS[verdict]}
    </span>
  );
}
