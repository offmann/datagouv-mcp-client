import { useMemo, useState } from 'react'

function formatEuro(n) {
  if (n >= 1e9) return `${(n / 1e9).toFixed(1)} MdEUR`
  if (n >= 1e6) return `${(n / 1e6).toFixed(0)} MEUR`
  if (n >= 1e3) return `${(n / 1e3).toFixed(0)} kEUR`
  return `${Math.round(n)} EUR`
}

export default function BudgetExplorer({ missions, totalBudget, taxResult }) {
  const [query, setQuery] = useState('')
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    return (missions || [])
      .filter((m) => m.value > 0)
      .filter((m) => !q || m.name.toLowerCase().includes(q))
      .map((m) => ({
        ...m,
        personalAmount: taxResult?.total ? (taxResult.total * m.value) / totalBudget : null,
      }))
  }, [missions, query, taxResult, totalBudget])

  if (!missions?.length) return null

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 mt-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-4">
        <h3 className="font-display text-2xl text-bleu-dark font-bold">Explorer les missions</h3>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Rechercher une mission"
          className="px-4 py-2 rounded-lg border border-gray-300 focus:border-bleu focus:outline-none"
        />
      </div>
      <div className="space-y-3">
        {filtered.slice(0, 15).map((mission, idx) => (
          <div key={mission.name} className="rounded-lg border border-gray-200 p-3">
            <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
              <p className="font-semibold text-gray-800">{idx + 1}. {mission.name}</p>
              <p className="text-sm text-gray-600">{mission.pct}% du budget</p>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2 mb-2">
              <div className="bg-bleu h-2 rounded-full" style={{ width: `${Math.min(100, mission.pct)}%` }} />
            </div>
            <p className="text-sm text-gray-700">
              Mission: <span className="font-semibold">{formatEuro(mission.value)}</span>
              {mission.personalAmount != null ? ` - Votre part estimee: ${formatEuro(mission.personalAmount)}` : ''}
            </p>
          </div>
        ))}
      </div>
      {filtered.length > 15 && (
        <p className="text-xs text-gray-500 mt-3">Affichage limite aux 15 premiers resultats.</p>
      )}
    </div>
  )
}
