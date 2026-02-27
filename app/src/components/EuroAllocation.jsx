import { useMemo } from 'react'

function formatEuro(n) {
  if (n >= 1e9) return `${(n / 1e9).toFixed(1)} MdEUR`
  if (n >= 1e6) return `${(n / 1e6).toFixed(0)} MEUR`
  if (n >= 1e3) return `${(n / 1e3).toFixed(0)} kEUR`
  return `${Math.round(n)} EUR`
}

export default function EuroAllocation({ missions, totalBudget, taxResult }) {
  const items = useMemo(() => {
    if (!missions?.length || !totalBudget) return []
    return missions
      .filter((m) => m.value > 0)
      .map((m) => ({
        name: m.name,
        per100: (100 * m.value) / totalBudget,
        personal: taxResult?.total ? (taxResult.total * m.value) / totalBudget : null,
      }))
      .sort((a, b) => b.per100 - a.per100)
      .slice(0, 8)
  }, [missions, totalBudget, taxResult])

  if (!items.length) return null

  return (
    <div className="bg-gradient-to-br from-bleu/10 to-white rounded-2xl border border-bleu/15 p-6 mt-6">
      <h3 className="font-display text-2xl font-bold text-bleu-dark mb-2">Sur 100 EUR de depenses publiques</h3>
      <p className="text-sm text-gray-600 mb-5">
        Allocation indicative selon la structure du budget de l'Etat.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {items.map((item) => (
          <div key={item.name} className="bg-white rounded-lg border border-gray-200 p-3">
            <p className="font-semibold text-gray-800 text-sm mb-1">{item.name}</p>
            <p className="text-bleu font-bold">{item.per100.toFixed(2)} EUR / 100 EUR</p>
            {item.personal != null && (
              <p className="text-xs text-gray-600 mt-1">Sur votre estimation: {formatEuro(item.personal)}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
