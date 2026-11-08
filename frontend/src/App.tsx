export default function App() {
  return (
    <div className="min-h-screen bg-bg text-slate-200 font-sans">
      <header className="border-b border-slate-800 bg-panel/80 px-6 py-4">
        <h1 className="text-xl font-semibold text-accent">SentinelForge</h1>
        <p className="text-sm text-slate-400">Cyber Security Vulnerability Assessment &amp; Penetration Testing Orchestration</p>
      </header>
      <main className="p-6 grid gap-4 md:grid-cols-3">
        <section className="bg-panel rounded-lg p-4 border border-slate-800 md:col-span-2">
          <h2 className="text-accent font-medium mb-2">SOC Dashboard (Scaffold)</h2>
          <p className="text-sm text-slate-400">Connect to the FastAPI backend at <code className="font-mono text-info">/api/v1</code> for engagements, assets, authorized scans, findings, and reports. Implement WebSocket live scan progress, Recharts risk/severity visualizations, and shadcn/ui components.</p>
        </section>
        <section className="bg-panel rounded-lg p-4 border border-slate-800">
          <h2 className="text-accent font-medium mb-2">Status</h2>
          <ul className="text-sm space-y-1">
            <li><span className="text-secure">●</span> Authorization gate: server-side</li>
            <li><span className="text-secure">●</span> Audit logging: enabled</li>
            <li><span className="text-warn">●</span> Nmap PoC connector: scaffolded</li>
          </ul>
        </section>
      </main>
    </div>
  )
}
