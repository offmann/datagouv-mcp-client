import { useMemo } from 'react'

function formatEuro(n) {
  if (n >= 1e9) return `${(n / 1e9).toFixed(1)} Md€`
  if (n >= 1e6) return `${(n / 1e6).toFixed(0)} M€`
  if (n >= 1e3) return `${(n / 1e3).toFixed(0)} k€`
  return `${Math.round(n)} €`
}

export default function PersonalImpact({ estimatedTax, missions, totalBudget }) {
  const breakdown = useMemo(() => {
    const totalContrib = estimatedTax?.total
    if (!totalContrib || !missions?.length || !totalBudget || totalBudget <= 0) return []
    return missions
      .filter(m => m.value > 0)
      .slice(0, 8)
      .map(m => ({
        name: m.name,
        amount: (totalContrib * m.value) / totalBudget,
        pct: m.pct,
      }))
      .filter(b => b.amount > 1)
  }, [estimatedTax, missions, totalBudget])

  if (breakdown.length === 0) return null

  return (
    <section className="py-12 px-4 md:px-8 max-w-2xl mx-auto">
      <div className="bg-gradient-to-br from-bleu/10 to-bleu/5 rounded-2xl p-8 border border-bleu/20">
        <h3 className="font-display text-xl font-bold text-bleu-dark mb-2">
          Où va votre contribution ?
        </h3>
        <p className="text-gray-600 text-sm mb-6">
          Sur vos {formatEuro(estimatedTax.total)} estimés, voici une répartition indicative par mission :
        </p>
        <ul className="space-y-3">
          {breakdown.map((item, i) => (
            <li key={i} className="flex justify-between items-center">
              <span className="text-gray-700">{item.name.length > 35 ? item.name.slice(0, 33) + '…' : item.name}</span>
              <span className="font-semibold text-bleu">{formatEuro(item.amount)}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
