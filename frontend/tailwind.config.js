/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        openshift: {
          red: '#EE0000',
          dark: '#1F1F1F',
          gray: '#292929',
        },
      },
    },
  },
  plugins: [],
};
