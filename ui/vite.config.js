import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/review/": "http://127.0.0.1:8000",
      "/github-review/": "http://127.0.0.1:8000",
      "/github-comment/": "http://127.0.0.1:8000"
    }
  }
});
