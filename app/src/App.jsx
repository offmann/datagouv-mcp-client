import { useState, useEffect } from 'react'
import Nav from './components/Nav'
import Hero from './components/Hero'
import TaxCalculator from './components/TaxCalculator'
import PersonalImpact from './components/PersonalImpact'
import BudgetTreemap from './components/BudgetTreemap'
import BudgetExplorer from './components/BudgetExplorer'
import RevenueBreakdown from './components/RevenueBreakdown'
import EuroAllocation from './components/EuroAllocation'
import EuropeChart from './components/EuropeChart'

function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [estimatedTax, setEstimatedTax] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('/data/public_spending.json')
      .then(r => r.json())
      .then(setData)
      .catch((e) => {
        console.error(e)
        setError(e?.message || 'Erreur de chargement')
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-bleu text-xl">Chargement des données...</div>
      </div>
    )
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center p-8">
        <p className="text-rouge">
          Impossible de charger les données ({error || 'inconnue'}). Lancez <code className="bg-white px-2 py-1 rounded">uv run python scripts/prepare_data.py</code>
        </p>
      </div>
    )
  }

  const { skyline, budget, recettes, meta } = data
  const generatedAt = meta?.generated_at_utc ? new Date(meta.generated_at_utc) : null
  const staleAfterDays = meta?.stale_after_days ?? 14
  const isStale = generatedAt ? ((Date.now() - generatedAt.getTime()) / (1000 * 60 * 60 * 24)) > staleAfterDays : false

  return (
    <div className="min-h-screen">
      <Nav />
      <Hero />
      <section className="px-4 md:px-8 max-w-6xl mx-auto -mt-4 mb-8">
        <div className={`rounded-xl border p-4 ${isStale ? 'bg-amber-50 border-amber-300' : 'bg-emerald-50 border-emerald-300'}`}>
          <p className="text-sm font-semibold text-gray-800 mb-1">
            {isStale ? 'Donnees potentiellement perimees' : 'Donnees recentes'}
          </p>
          <p className="text-sm text-gray-700">
            Derniere generation: {generatedAt ? generatedAt.toLocaleString('fr-FR') : 'inconnue'}.
            Seuil de fraicheur: {staleAfterDays} jours.
          </p>
          <p className="text-xs text-gray-600 mt-2">
            Annees couvrees - Recettes: {meta?.coverage_years?.recettes || '?'} | Budget: {meta?.coverage_years?.budget || '?'} | Europe: {meta?.coverage_years?.skyline || '?'}
          </p>
        </div>
      </section>
      <TaxCalculator totalRecettes={recettes?.total} onCalculate={setEstimatedTax} />
      <PersonalImpact estimatedTax={estimatedTax} missions={budget?.missions} totalBudget={budget?.total} />

      {/* Chapitre 1: D'où viennent vos impôts ? */}
      <section id="recettes" className="py-20 px-4 md:px-8 max-w-6xl mx-auto">
        <h2 className="font-display text-3xl md:text-4xl font-bold text-bleu-dark mb-4">
          D'où viennent vos impôts ?
        </h2>
        <p className="text-lg text-gray-600 mb-10 max-w-2xl">
          Le budget de l'État est financé par les recettes fiscales. Vue lisible des principales sources (PLF 2024), avec filtres interactifs.
        </p>
        <RevenueBreakdown revenues={recettes?.recettes || []} />
      </section>

      {/* Chapitre 2: Où va chaque euro ? */}
      <section id="budget" className="py-20 px-4 md:px-8 max-w-6xl mx-auto bg-white/50">
        <h2 className="font-display text-3xl md:text-4xl font-bold text-bleu-dark mb-4">
          Où va chaque euro ?
        </h2>
        <p className="text-lg text-gray-600 mb-10 max-w-2xl">
          Le budget de l'État 2025 est réparti en missions. Cliquez pour explorer les principales dépenses publiques.
        </p>
        <BudgetTreemap missions={budget?.missions || []} total={budget?.total} />
        <EuroAllocation missions={budget?.missions || []} totalBudget={budget?.total} taxResult={estimatedTax} />
        <BudgetExplorer missions={budget?.missions || []} totalBudget={budget?.total} taxResult={estimatedTax} />
      </section>

      {/* Chapitre 3: France vs Europe */}
      <section id="europe" className="py-20 px-4 md:px-8 max-w-6xl mx-auto">
        <h2 className="font-display text-3xl md:text-4xl font-bold text-bleu-dark mb-4">
          Et nos voisins européens ?
        </h2>
        <p className="text-lg text-gray-600 mb-10 max-w-2xl">
          Comparaison des dépenses publiques (% du PIB) entre la France et ses voisins. Les montants sont en % du PIB potentiel.
        </p>
        <EuropeChart data={skyline?.europe_comparison} colors={['#0055A4', '#4A90D9', '#7BB3E8', '#E63946', '#2D6A4F', '#52B788']} />
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 bg-bleu-dark text-white">
        <div className="max-w-6xl mx-auto">
          <p className="font-display text-xl font-semibold mb-4">Où va votre argent ?</p>
          <div className="text-sm opacity-90 mb-4 space-y-2">
            <p>
              Données issues de <a href="https://www.data.gouv.fr" target="_blank" rel="noopener noreferrer" className="underline">data.gouv.fr</a>.
            </p>
            {(meta?.sources ? Object.values(meta.sources) : []).map((source) => (
              <p key={source.resource_url}>
                {source.label} ({source.fetch_method || 'unknown'}) - <a href={source.resource_url} target="_blank" rel="noopener noreferrer" className="underline">ressource</a> - <a href={source.dataset_url} target="_blank" rel="noopener noreferrer" className="underline">dataset</a>
              </p>
            ))}
          </div>
          <p className="text-xs opacity-75">Les montants sont des estimations. Données à caractère indicatif.</p>
        </div>
      </footer>
    </div>
  )
}

export default App
