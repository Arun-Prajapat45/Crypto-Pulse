import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  optimizeDeps: {
    include: ["fast-equals"],
    esbuildOptions: {
      mainFields: ["module", "main"],
    },
  },

  build: {
    commonjsOptions: {
      transformMixedEsModules: true,
    },
  },

  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/news": { target: "http://localhost:8000", changeOrigin: true },
      "/auth": { target: "http://localhost:8000", changeOrigin: true },
      "/forecast": { target: "http://localhost:8000", changeOrigin: true },
      "/dashboard": { target: "http://localhost:8000", changeOrigin: true },
      "/profile": { target: "http://localhost:8000", changeOrigin: true },
      "/uploads": { target: "http://localhost:8000", changeOrigin: true },
      "/profilephotos": { target: "http://localhost:8000", changeOrigin: true },
    },
  },
});