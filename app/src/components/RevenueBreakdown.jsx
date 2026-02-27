import { useMemo, useState } from 'react'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell } from 'recharts'

const COLORS = ['#0055A4', '#2D6A4F', '#4A90D9', '#E63946', '#7BB3E8', '#52B788', '#FF6B6B', '#9D4EDD']

function formatEuro(n) {
  if (n >= 1e9) return `${(n / 1e9).toFixed(1)} MdEUR`
  if (n >= 1e6) return `${(n / 1e6).toFixed(0)} MEUR`
  return `${Math.round(n / 1e3)} kEUR`
}

export default function RevenueBreakdown({ revenues }) {
  const [mode, setMode] = useState('top8')

  const chartData = useMemo(() => {
    const list = [...(revenues || [])].sort((a, b) => b.value - a.value)
    if (mode === 'all') return list
    if (mode === 'pct2') return list.filter((r) => r.pct >= 2)
    const top = list.slice(0, 8)
    const rest = list.slice(8)
    const restTotal = rest.reduce((acc, item) => acc + item.value, 0)
    const restPct = rest.reduce((acc, item) => acc + item.pct, 0)
    return rest.length > 0 ? [...top, { name: 'Autres recettes', value: restTotal, pct: Number(restPct.toFixed(1)) }] : top
  }, [revenues, mode])

  if (!chartData.length) return null

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 md:p-8">
      <div className="flex flex-wrap gap-2 mb-5">
        <button className={`px-3 py-1.5 rounded-full text-sm ${mode === 'top8' ? 'bg-bleu text-white' : 'bg-gray-100 text-gray-700'}`} onClick={() => setMode('top8')}>Top 8 + autres</button>
        <button className={`px-3 py-1.5 rounded-full text-sm ${mode === 'pct2' ? 'bg-bleu text-white' : 'bg-gray-100 text-gray-700'}`} onClick={() => setMode('pct2')}>Parts ≥ 2%</button>
        <button className={`px-3 py-1.5 rounded-full text-sm ${mode === 'all' ? 'bg-bleu text-white' : 'bg-gray-100 text-gray-700'}`} onClick={() => setMode('all')}>Tout afficher</button>
      </div>
      <div className="h-[460px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ left: 12, right: 16 }}>
            <XAxis type="number" tickFormatter={(v) => `${v}%`} domain={[0, 'auto']} />
            <YAxis type="category" dataKey="name" width={210} tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(value, _, item) => [`${formatEuro(value)} (${item?.payload?.pct}%)`, 'Montant']}
              contentStyle={{ borderRadius: 10 }}
            />
            <Bar dataKey="pct" radius={[0, 6, 6, 0]}>
              {chartData.map((entry, i) => (
                <Cell key={entry.name} fill={COLORS[i % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="text-xs text-gray-500 mt-2">
        Astuce: passez en mode "Top 8 + autres" pour une lecture rapide, puis "Tout afficher" pour le détail complet.
      </p>
    </div>
  )
}
