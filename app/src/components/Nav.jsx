import { useState } from 'react'

const LINKS = [
  { href: '#', label: 'Accueil' },
  { href: '#recettes', label: 'Vos impôts' },
  { href: '#budget', label: 'Le budget' },
  { href: '#europe', label: 'France vs Europe' },
]

export default function Nav() {
  const [open, setOpen] = useState(false)

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-gray-100">
      <div className="max-w-6xl mx-auto px-4 flex items-center justify-between h-14">
        <a href="#" className="font-display font-bold text-bleu text-lg">
          Où va votre argent ?
        </a>
        <div className="hidden md:flex gap-6">
          {LINKS.map(({ href, label }) => (
            <a key={href} href={href} className="text-gray-600 hover:text-bleu transition-colors text-sm font-medium">
              {label}
            </a>
          ))}
        </div>
        <button
          className="md:hidden p-2"
          onClick={() => setOpen(!open)}
          aria-label="Menu"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {open ? <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /> : <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />}
          </svg>
        </button>
      </div>
      {open && (
        <div className="md:hidden border-t border-gray-100 py-4 px-4 flex flex-col gap-2">
          {LINKS.map(({ href, label }) => (
            <a key={href} href={href} className="text-gray-600 hover:text-bleu" onClick={() => setOpen(false)}>
              {label}
            </a>
          ))}
        </div>
      )}
    </nav>
  )
}
