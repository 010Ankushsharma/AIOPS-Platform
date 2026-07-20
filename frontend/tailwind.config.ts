import type { Config } from "tailwindcss";

export default {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        brand: { red: "#FF000F", lilac: "#6764f6" },
      },
    },
  },
  plugins: [],
} satisfies Config;
