# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/resources/webapps/recon/ozone-recon-web/src/__tests__/Overview.test.tsx


Purpose: Vitest/Testing Library coverage for the V2 Overview page under both populated and null/faulty API scenarios.

Important APIs/types/functions: Defines `WrappedOverviewComponent` with `BrowserRouter`, mocks `@/v2/components/eChart/eChart`, uses `overviewServer` and `faultyOverviewServer`, and asserts locator constants from `overviewLocators`.

Control flow/state/persistence: `describe.each([true,false])` starts the appropriate MSW server, renders once per scenario, waits 100 ms for requests/state, then checks card text. Cleanup is intentionally deferred with `dont-cleanup-after-each` and done in `afterAll`.

Dependencies/integration points: Exercises `/api/v1/clusterState`, `/api/v1/task/status`, `/api/v1/keys/open/summary`, and `/api/v1/keys/deletePending/summary` through MSW and the real V2 overview component.

Risks/test signals: The fixed timeout can be flaky compared with `findBy`/`waitFor`; skipped cleanup trades speed for possible cross-test coupling. Tests strongly signal expected fallback strings: `N/A` and zero-byte capacity values.
