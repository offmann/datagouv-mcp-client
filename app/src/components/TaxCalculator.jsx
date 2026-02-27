import { useState } from 'react'

const BRACKETS = [
  { upTo: 11294, rate: 0.0 },
  { upTo: 28797, rate: 0.11 },
  { upTo: 82341, rate: 0.3 },
  { upTo: 177106, rate: 0.41 },
  { upTo: Infinity, rate: 0.45 },
]

const SOCIAL_CONTRIB_RATE = 0.17
const VAT_EFFECTIVE_RATE = 0.12

function computeProgressiveTax(base) {
  let tax = 0
  let previous = 0
  for (const bracket of BRACKETS) {
    const upper = Math.min(base, bracket.upTo)
    const taxable = Math.max(0, upper - previous)
    tax += taxable * bracket.rate
    previous = bracket.upTo
    if (base <= bracket.upTo) break
  }
  return tax
}

export default function TaxCalculator({ totalRecettes, onCalculate }) {
  const [income, setIncome] = useState('')
  const [consumptionRate, setConsumptionRate] = useState(75)
  const [showResult, setShowResult] = useState(false)

  const incomeNum = parseFloat(income.replace(/\s/g, '')) || 0
  const taxableBase = Math.max(0, incomeNum * 0.9)
  const incomeTax = computeProgressiveTax(taxableBase)
  const socialContrib = incomeNum * SOCIAL_CONTRIB_RATE
  const vat = incomeNum * (consumptionRate / 100) * VAT_EFFECTIVE_RATE
  const totalContrib = incomeTax + socialContrib + vat

  const handleCalculate = () => {
    setShowResult(true)
    if (incomeNum > 0 && onCalculate) {
      onCalculate({
        income: incomeNum,
        total: totalContrib,
        monthly: totalContrib / 12,
        components: [
          { label: 'Impot sur le revenu (bareme simplifie)', value: incomeTax },
          { label: 'Contributions sociales (proxy)', value: socialContrib },
          { label: 'TVA estimee sur consommation', value: vat },
        ],
        assumptions: [
          'Abattement de 10% applique sur le revenu imposable',
          `Taux de consommation retenu: ${consumptionRate}%`,
          'TVA effective moyenne: 12% des depenses',
        ],
      })
    }
  }

  const formatNum = (n) => {
    if (n >= 1e9) return `${(n / 1e9).toFixed(1)} milliard`
    if (n >= 1e6) return `${(n / 1e6).toFixed(0)} million`
    return new Intl.NumberFormat('fr-FR').format(Math.round(n))
  }

  return (
    <section className="py-16 px-4 md:px-8 max-w-2xl mx-auto">
      <div className="bg-white rounded-2xl shadow-xl p-8 border border-bleu/10">
        <h2 className="font-display text-2xl font-bold text-bleu-dark mb-2">
          Combien payez-vous ?
        </h2>
        <p className="text-gray-600 mb-6">
          Entrez votre revenu annuel pour une estimation transparente de votre contribution fiscale.
        </p>
        <div className="flex flex-col sm:flex-row gap-4">
          <input
            type="text"
            inputMode="numeric"
            placeholder="Ex: 35 000"
            value={income}
            onChange={(e) => {
              setIncome(e.target.value.replace(/[^\d\s]/g, ''))
              setShowResult(false)
            }}
            onKeyDown={(e) => e.key === 'Enter' && handleCalculate()}
            className="flex-1 px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-bleu focus:outline-none text-lg"
          />
          <button
            onClick={handleCalculate}
            className="px-6 py-3 bg-bleu text-white rounded-xl font-semibold hover:bg-bleu-dark transition-colors"
          >
            Calculer
          </button>
        </div>
        <div className="mt-5">
          <label className="block text-sm text-gray-600 mb-2">
            Part du revenu consommee (pour estimer la TVA): <span className="font-semibold text-bleu-dark">{consumptionRate}%</span>
          </label>
          <input
            type="range"
            min={40}
            max={95}
            step={5}
            value={consumptionRate}
            onChange={(e) => {
              setConsumptionRate(parseInt(e.target.value, 10))
              setShowResult(false)
            }}
            className="w-full accent-bleu"
          />
        </div>
        {showResult && incomeNum > 0 && (
          <div className="mt-8 p-6 bg-bleu/5 rounded-xl border border-bleu/20">
            <p className="text-bleu-dark font-semibold mb-2">
              Estimation annuelle de vos contributions fiscales : <span className="text-bleu text-xl">{formatNum(totalContrib)} €</span>
            </p>
            <p className="text-sm text-gray-600 mb-3">
              Soit environ <span className="font-semibold">{formatNum(totalContrib / 12)} €</span> par mois. Budget total de l'État 2024: {totalRecettes ? formatNum(totalRecettes) + ' €' : '...'}.
            </p>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>IR simplifie: {formatNum(incomeTax)} €</li>
              <li>Contributions sociales: {formatNum(socialContrib)} €</li>
              <li>TVA estimee: {formatNum(vat)} €</li>
            </ul>
          </div>
        )}
      </div>
    </section>
  )
}
