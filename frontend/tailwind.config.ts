import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0A0E14',
        panel: '#121821',
        accent: '#00F0FF',
        secure: '#39FF14',
        critical: '#FF1744',
        high: '#FF6D00',
        medium: '#FFD600',
        low: '#00E676',
        info: '#00B8D4',
        warn: '#FFB300'
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        sans: ['Inter', 'system-ui', 'sans-serif']
      }
    }
  },
  plugins: []
} satisfies Config
