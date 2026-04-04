export default function AboutPage() {
  return (
    <div className="max-w-3xl mx-auto space-y-8 py-8">
      <h1 className="text-3xl font-bold">How it works</h1>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">What is the Policy Verdict Engine?</h2>
        <p className="text-gray-700 leading-relaxed">
          The Policy Verdict Engine is an AI-powered tool that evaluates
          government policies against peer-reviewed academic evidence. It is not
          an opinion platform — it is an evidence aggregator with an AI reasoning
          layer. The verdict comes from the literature, not from the model&apos;s
          training weights.
        </p>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Methodology</h2>
        <ol className="list-decimal list-inside space-y-2 text-gray-700">
          <li>
            <strong>Policy parsing:</strong> Your submitted policy is analyzed to
            extract key claims and topics.
          </li>
          <li>
            <strong>Academic search:</strong> The system queries Semantic Scholar,
            OpenAlex, and PubMed for peer-reviewed papers relevant to the
            policy&apos;s claims.
          </li>
          <li>
            <strong>Relevance ranking:</strong> Retrieved abstracts are embedded
            and ranked by semantic similarity to the policy text. The top 10 most
            relevant papers are selected.
          </li>
          <li>
            <strong>Verdict generation:</strong> An AI model reads ONLY the
            selected abstracts and evaluates whether the academic evidence
            supports, contradicts, or is mixed on the policy. It is explicitly
            instructed not to use prior knowledge.
          </li>
        </ol>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Verdict categories</h2>
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <span className="inline-block px-3 py-1 text-sm font-bold rounded-full bg-green-100 text-green-800 border border-green-300">
              SMART
            </span>
            <span className="text-gray-700">
              Academic evidence broadly supports this policy
            </span>
          </div>
          <div className="flex items-center gap-3">
            <span className="inline-block px-3 py-1 text-sm font-bold rounded-full bg-amber-100 text-amber-800 border border-amber-300">
              MIXED
            </span>
            <span className="text-gray-700">
              Evidence is mixed, insufficient, or contradictory
            </span>
          </div>
          <div className="flex items-center gap-3">
            <span className="inline-block px-3 py-1 text-sm font-bold rounded-full bg-red-100 text-red-800 border border-red-300">
              POOR
            </span>
            <span className="text-gray-700">
              Academic evidence contradicts this policy
            </span>
          </div>
        </div>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Limitations</h2>
        <ul className="list-disc list-inside space-y-1 text-gray-700">
          <li>Only uses publicly available abstracts (not full papers)</li>
          <li>
            Coverage depends on what is indexed in Semantic Scholar, OpenAlex, and
            PubMed
          </li>
          <li>
            Niche or highly local policies may have little academic coverage
          </li>
          <li>
            This is an automated analysis — not a substitute for expert review
          </li>
          <li>
            The system is honest about uncertainty: if evidence is thin, the
            verdict says so
          </li>
        </ul>
      </section>

      <section className="space-y-3">
        <h2 className="text-xl font-semibold">Data &amp; transparency</h2>
        <p className="text-gray-700 leading-relaxed">
          All verdicts are public by default. Every verdict page shows the exact
          sources used, with DOI links to the original papers. No editorial
          filtering is applied — the system presents what the literature says.
        </p>
      </section>
    </div>
  );
}
