# sources/test-tools/syzkaller/syz-cluster/dashboard/local_ui_test.go

## Purpose
Provides an opt-in manual UI fixture for running the dashboard locally with realistic test data.

## Important APIs, types, and functions
Defines flags `-local-ui` and `-local-ui-addr`. `TestLocalUI` skips unless explicitly enabled, requires verbose mode and no test timeout, populates the database, starts a TCP listener, and serves `handler.Mux()`. `populateData` uploads a dummy series, triage log, build, session tests, findings, grouped test steps, reports, moderation/upstream transitions, and a patch-test job.

## Control flow
The test builds an in-process test environment and controller server, uses controller/client APIs to create dashboard data, runs reporter generation and confirmation paths so stats and reports appear, submits a job, then blocks in `http.Serve` for browser inspection.

## State and persistence behavior
All state is created in the test Spanner/blob environment. Blob storage stores the fake triage log and uploaded logs/artifacts through controller APIs. The session is explicitly marked finished so generated reports and stats can be visible.

## Dependencies and integration points
Depends on controller upload helpers, reporter generation/server helpers, dashboard handler construction, `pkg/db` repository updates, and `pkg/api` types. It integrates the dashboard with almost the full local syz-cluster data flow.

## Risks and edge cases
This is intentionally not a normal automated test. It fails if run with a timeout or without `-v`, then blocks forever until killed. It binds a configurable local address and can conflict with an existing process. Because the data is synthetic, it is useful for UI coverage but not for production-scale performance.

## Test signals
High manual signal for visual dashboard behavior across series, findings, logs, test steps, reports, and jobs. It is skipped in default test runs, so automated CI signal comes from other tests.
