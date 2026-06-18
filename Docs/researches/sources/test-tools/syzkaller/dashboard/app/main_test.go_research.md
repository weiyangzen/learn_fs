# sources/test-tools/syzkaller/dashboard/app/main_test.go

## Purpose

`main_test.go` is a black-box integration-style test suite for the dashboard web UI handlers in `main.go`. It uses the local dashboard test harness to upload builds and crashes, advance fake time, poll reportings, call authenticated HTTP routes, and assert rendered page behavior.

## Important APIs, Types, and Functions

Tests use `NewCtx`, `NewSpannerCtx`, `Ctx.AuthGET`, `Ctx.GET`, test clients such as `c.client`, `c.client2`, `c.publicClient`, and helpers like `testBuild`, `testCrash`, `testCrashWithRepro`, `pollEmailBug`, `globalClient.pollBugs`, and `globalClient.updateBug`. The file defines constants `subsystemA` and `subsystemB` used by subsystem inference fixtures.

Individual tests cover:

- `TestOnlyManagerFilter` for `only_manager` filtering on open and invalid pages.
- `TestSubsystemFilterMain` and `TestSubsystemFilterTerminal` for label-based subsystem filters.
- `TestMainBugFilters` for no-subsystem, with-repro, with-AI-patch, and filter banner behavior.
- `TestSubsystemsList`, `TestSubsystemPage`, and `TestSubsystemsPageRedirect` for subsystem list filtering, per-subsystem pages, and redirect configuration.
- `TestMultiLabelFilter` for combined label filtering and drop-label link behavior.
- `TestAdminJobList` for admin bisection job list links.
- `TestNoThrottle` and `TestThrottle` for request throttling behavior.
- `TestManagerPage` and `TestReproSubmitAccess` for manager build history, unknown manager errors, and repro request access.

## Control Flow

Most tests construct datastore state by uploading builds and reporting crashes, optionally poll bugs so reporting IDs and labels are initialized, and then call dashboard routes with different access levels and query parameters. Assertions are primarily string containment checks against rendered HTML, plus `HTTPError` checks for expected redirects, bad requests, or rate limiting.

## State and Persistence Behavior

The tests exercise datastore writes for builds, crashes, bugs, reporting state, jobs, labels, subsystem cache, and repro tasks through the same client APIs used by dashboard components. `TestSubsystemsList` explicitly triggers `/cron/refresh_subsystems` before checking subsystem cache output. `TestThrottle` mutates config through `transformContext` to enable a short throttle window in the test context.

## Dependencies and Integration Points

This suite depends on the test App Engine context, dashboard config fixtures, subsystem inference fixtures that map guilty files to `subsystemA` and `subsystemB`, email/global reporting helpers, and HTTP wrapper behavior that returns `HTTPError` values. It validates the integration among `main.go`, reporting state, datastore entities, cache refresh, throttle logic, and template output.

## Risks and Test Signals

The tests catch regressions where filters disappear from query construction, multi-label filters are treated as OR instead of AND, filtered pages still show unrelated managers, subsystem redirects break, or access levels expose repro submission to public users. They are less precise about HTML structure because most assertions are content-based. They do not deeply validate JSON fields, asset links, Cloud Logging, text blob access, or all admin actions, so those remain residual risk areas.
