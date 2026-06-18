# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/tsconfig.json

## Purpose
This TypeScript configuration defines the compile-time contract for the Recon Vite/React frontend. It type-checks source files under `src` without emitting output.

## Important options
The target is `es2015`, with `dom`, `dom.iterable`, and `esnext` libs. TypeScript is strict, JavaScript input is disabled, module output is `esnext`, module resolution is `node`, JSON modules are allowed, and `isolatedModules` plus `noEmit` suit Vite/SWC builds. `baseUrl` is `src`; path aliases map `@/*` to source-root imports and `@tests/*` to `src/__tests__/*`. Global types include Vite, SVGR, and Vitest globals.

## Control flow, state, and persistence
This file has no runtime control flow or persistence. Its practical effect is compile-time enforcement and IDE/module resolution behavior.

## Dependencies and integration points
It aligns with `vite.config.ts`, which defines matching `@` and `@tests` aliases and Vitest setup. The React JSX setting is `react`, matching classic JSX transform expectations while Vite uses `@vitejs/plugin-react-swc`.

## Risks and edge cases
`skipLibCheck` speeds builds but can hide dependency type conflicts. `isolatedModules` is necessary for Vite-style transpilation but disallows some TypeScript patterns. Strict mode exposes the inaccurate table row types seen in `pipelines.tsx`, though some `any` and widened column types bypass that protection.

## Test signals
No direct test file targets this config. Signals are frontend type-check/build success and Vitest discovery of `src/__tests__/**/*.test.tsx`.
