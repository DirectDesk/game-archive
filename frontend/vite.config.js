import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({ plugins: [vue()], server: { proxy: { '/api': 'http://localhost:8000', '/data': 'http://localhost:8000' } } })
