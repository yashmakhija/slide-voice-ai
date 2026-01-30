import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "path";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/ws": {
        target: "wss://slide-api.iyash.me",
        ws: true,
      },
      "/api": {
        target: "https://slide-api.iyash.me",
      },
    },
  },
});
