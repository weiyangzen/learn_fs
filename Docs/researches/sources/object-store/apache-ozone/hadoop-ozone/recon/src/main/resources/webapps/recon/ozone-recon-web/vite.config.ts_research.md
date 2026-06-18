# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/vite.config.ts

## Purpose
This Vite configuration builds and serves the Recon frontend. It configures React/SWC, static asset layout compatible with the existing webapp packaging, local API proxying, Less theming, aliases, and Vitest.

## Important APIs and options
`defineConfig` returns the Vite config. `pathResolve` resolves aliases relative to the project directory. `base: ""` makes assets relative so the app works behind a proxy or non-root path. Plugins include `react({ devTarget: "es2015" })` and `splitVendorChunkPlugin`. Build output targets ES2015, writes to `build`, and places JS under `static/js`, CSS under `static/css`, and other assets under `static/media`. Dev server proxies `/api` to `http://localhost:9888`. Less enables JavaScript, always-on math, relative URLs, and primary color override.

## Control flow, state, and persistence
Runtime control flow is limited to Vite's build/dev server lifecycle and the `assetFileNames` callback. There is no application state.

## Dependencies and integration points
The config integrates Vite, `@vitejs/plugin-react-swc`, Rollup output naming, Ant Design Less variables, and Vitest with jsdom setup at `src/__tests__/vitest.setup.ts`. It mirrors `tsconfig.json` aliases and supports SVG imports through the types listed there.

## Risks and edge cases
`assetInfo.name!.split(".")[1]` assumes an asset name exists and has a simple extension; multi-dot names use the second segment rather than the last extension. `base: ""` is intentional for proxy deployment, but can alter assumptions for absolute URLs. The dev proxy is fixed to localhost port 9888. `splitVendorChunkPlugin` is legacy but still usable in Vite projects.

## Test signals
Vitest is configured for `src/__tests__/**/*.test.tsx` with verbose reporting and jsdom. Build success confirms asset callback and Less preprocessing behavior.
