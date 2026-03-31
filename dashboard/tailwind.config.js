/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        zt: {
          bg:       '#0f1117',
          surface:  '#1a1d27',
          border:   '#2a2d3a',
          purple:   '#7c6fef',
          teal:     '#1d9e75',
          amber:    '#f59e0b',
          red:      '#ef4444',
          green:    '#22c55e',
          muted:    '#6b7280',
          text:     '#e2e8f0',
        },
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
