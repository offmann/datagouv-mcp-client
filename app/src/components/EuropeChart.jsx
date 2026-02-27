import { useMemo } from 'react'
import { BarChart, Bar, XAxis, YAxis, Legend, ResponsiveContainer, Tooltip } from 'recharts'

export default function EuropeChart({ data, colors }) {
  const chartData = useMemo(() => {
    if (!data) return []
    return Object.entries(data).map(([pays, cats]) => ({
      pays,
      ...Object.fromEntries(Object.entries(cats).filter(([, v]) => v != null && !Number.isNaN(v))),
    }))
  }, [data])

  const categories = useMemo(() => {
    if (!data?.France) return []
    return Object.keys(data.France).filter(k => data.France[k] != null && !Number.isNaN(data.France[k]))
  }, [data])

  if (chartData.length === 0 || categories.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-8 h-96 flex items-center justify-center text-gray-500">
        Aucune donnée de comparaison disponible
      </div>
    )
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 md:p-8 overflow-x-auto">
      <div className="h-96 min-w-[400px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ left: 70, right: 30 }}>
            <XAxis type="number" unit=" %" domain={[0, 'auto']} />
            <YAxis type="category" dataKey="pays" width={70} tick={{ fontSize: 12 }} />
            <Tooltip formatter={(v) => `${Number(v).toFixed(1)} %`} contentStyle={{ borderRadius: 8 }} />
            <Legend />
            {categories.map((cat, i) => (
              <Bar key={cat} dataKey={cat} fill={colors[i % colors.length]} stackId="a" name={cat} />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
