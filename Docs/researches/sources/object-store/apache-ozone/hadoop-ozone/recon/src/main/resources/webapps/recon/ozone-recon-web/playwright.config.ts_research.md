# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/playwright.config.ts

## Purpose

`playwright.config.ts` defines the Playwright test runner configuration for Recon web UI E2E tests. It points tests at the local Vite app, configures Chromium as the only browser project, controls CI retries/workers, enables HTML reporting, and starts the dev server automatically for test runs.

## Important APIs, Types, and Configuration

The file imports `defineConfig` and `devices` from `@playwright/test`. It sets `testDir: './e2e'`, `fullyParallel: true`, `forbidOnly` in CI, `retries` to 2 in CI and 0 locally, `workers` to 1 in CI and default locally, `reporter: 'html'`, `baseURL: 'http://localhost:3000'`, and `trace: 'on-first-retry'`. The only project is `chromium` using `devices['Desktop Chrome']`. The managed web server runs `pnpm start`, waits on `http://localhost:3000`, and reuses existing local servers outside CI.

## Control Flow

When `pnpm e2e` runs, Playwright starts or reuses the Vite server, waits for the configured URL, discovers tests under `./e2e`, and executes them in Desktop Chrome. Relative navigations such as `page.goto('/#/Assistant')` resolve against `baseURL`. On first retry, traces are captured for debugging. Results are emitted through the HTML reporter.

## State and Persistence Behavior

This file stores static runner configuration. Runtime state includes Playwright reports, retry traces, screenshots created by tests, and browser contexts/pages. CI behavior is controlled by `process.env.CI`: retries, one worker, `.only` protection, and no server reuse.

## Dependencies and Integration Points

This config depends on `@playwright/test`, the `start` script in `package.json`, E2E specs under `e2e`, the React app serving hash routes from Vite, and any network stubbing or backend setup performed by individual tests. It does not start json-server, so tests that need mock API data must stub routes or arrange the mock/backend separately.

## Risks

`fullyParallel: true` can expose shared artifact or backend-state conflicts. Local parallelism differs from CI's single worker. The web server command starts only Vite, not `pnpm dev`, so tests depending on `api/routes.json` or `pagination.js` can fail unless they stub calls or a mock API is already running. Reusing an existing local server can hide environment drift. Only Chromium is covered, so Firefox, WebKit, and mobile regressions are not tested by default.

## Test Signals

The main signal is a successful `pnpm e2e` run. In CI, retry traces and the HTML report help debug failures. Broader browser confidence would require adding more Playwright projects.
