export default function Hero() {
  return (
    <header className="relative min-h-[85vh] flex flex-col items-center justify-center px-4 overflow-hidden pt-14">
      <div className="absolute inset-0 bg-gradient-to-br from-bleu/10 via-creme to-rouge/5" />
      <div className="relative z-10 text-center max-w-4xl mx-auto">
        <p className="text-bleu font-medium uppercase tracking-widest text-sm mb-4">
          Transparence budgétaire
        </p>
        <h1 className="font-display text-5xl md:text-7xl font-bold text-bleu-dark leading-tight mb-6">
          Où va votre argent ?
        </h1>
        <p className="text-xl md:text-2xl text-gray-600 mb-10 max-w-2xl mx-auto">
          Chaque euro que vous payez en impôts finance des politiques publiques. Découvrez comment l'État utilise le budget national.
        </p>
        <a
          href="#recettes"
          className="inline-flex items-center gap-2 bg-bleu text-white px-8 py-4 rounded-full font-semibold hover:bg-bleu-dark transition-colors shadow-lg"
        >
          Explorer le budget
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </a>
      </div>
    </header>
  )
}
