import SubmitForm from "@/components/SubmitForm";
import RecentVerdicts from "@/components/RecentVerdicts";

export default function Home() {
  return (
    <div className="space-y-12">
      <section className="text-center space-y-4 pt-8">
        <h1 className="text-4xl font-bold tracking-tight">
          Evaluate any policy against the evidence
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Submit a government policy and get a verdict backed by peer-reviewed
          academic research. No opinions — just evidence.
        </p>
      </section>

      <section className="max-w-2xl mx-auto">
        <SubmitForm />
      </section>

      <section>
        <h2 className="text-2xl font-bold mb-6">Recent verdicts</h2>
        <RecentVerdicts />
      </section>
    </div>
  );
}
