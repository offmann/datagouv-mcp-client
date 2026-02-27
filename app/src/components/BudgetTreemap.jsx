import { Treemap, ResponsiveContainer, Tooltip } from 'recharts'

const COLORS = ['#0055A4', '#2D6A4F', '#9D4EDD', '#E63946', '#F77F00', '#4A90D9', '#40916C', '#C77DFF', '#FF6B6B', '#FCBF49', '#52B788', '#7BB3E8']

function formatEuro(n) {
  if (n >= 1e9) return `${(n / 1e9).toFixed(1)} Md€`
  if (n >= 1e6) return `${(n / 1e6).toFixed(0)} M€`
  return `${Math.round(n / 1e3)} k€`
}

const CustomContent = (props) => {
  const { x, y, width, height, name, value, index } = props
  const fontSize = Math.min(14, Math.min(width, height) / 6)
  const showLabel = width > 70 && height > 25

  if (!name || name === 'Budget') return null

  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        fill={COLORS[(index || 0) % COLORS.length]}
        fillOpacity={0.9}
        stroke="#fff"
        strokeWidth={2}
        rx={4}
      />
      {showLabel && (
        <>
          <text x={x + width / 2} y={y + height / 2 - 4} textAnchor="middle" fill="#fff" fontSize={fontSize} fontWeight={600}>
            {name?.length > 22 ? name.slice(0, 20) + '…' : name}
          </text>
          <text x={x + width / 2} y={y + height / 2 + fontSize} textAnchor="middle" fill="rgba(255,255,255,0.95)" fontSize={fontSize - 2}>
            {formatEuro(value)}
          </text>
        </>
      )}
    </g>
  )
}

export default function BudgetTreemap({ missions, total }) {
  const children = missions
    .filter(m => m.value > 0)
    .map((m, i) => ({
      name: m.name,
      size: m.value,
      fill: COLORS[i % COLORS.length],
    }))

  if (children.length === 0) {
    return (
      <div className="bg-gray-100 rounded-xl h-64 flex items-center justify-center text-gray-500">
        Aucune donnée disponible
      </div>
    )
  }

  const treeData = [{ name: 'Budget', children }]

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <Treemap
            data={treeData}
            dataKey="size"
            aspectRatio={4 / 3}
            stroke="#fff"
            content={<CustomContent />}
          >
            <Tooltip formatter={(v) => formatEuro(v)} contentStyle={{ borderRadius: 8 }} />
          </Treemap>
        </ResponsiveContainer>
      </div>
      {total && (
        <p className="mt-4 text-sm text-gray-500 text-center">
          Budget total : {formatEuro(total)} (crédits de paiement PLF 2025)
        </p>
      )}
    </div>
  )
}
