# sources/test-tools/syzkaller/dashboard/app/app_test.go

## Purpose

`app_test.go` defines the dashboard test configuration, shared test data builders, and core end-to-end tests for App Engine dashboard behavior. It is foundational test infrastructure for the other files in this subset because it installs `testConfig`, registers namespaces/clients, and provides canonical build/crash factories.

## Important setup, helpers, and tests

- `init` sets App Engine version environment variables, resets mock globals, installs local/test config, and copies local UI namespaces into `testConfig`.
- `testConfig` is a large `GlobalConfig` with ACLs, global clients, namespace clients, reporting configs, AI namespace `ains`, repository configs, managers, subsystem services, coverage config, and access-level test namespaces.
- `testSubsystems`, client/key constants, `skipWithRepro`, `skipWithRepro2`, and `TestConfig` support reporting and subsystem tests.
- `testBuild`, `testCrash`, `testCrashWithRepro`, and `testCrashID` create deterministic `dashapi` objects.
- `TestApp` exercises basic routing, client auth failures, build upload idempotency, namespace isolation, crash reporting, crash purging trigger, failed repro reporting, polling, and reporting update.
- `TestRedirects` and `TestResponseStatusCode` check UI redirect/status behavior.
- `TestPurgeOldCrashes` validates crash retention policy for reported, repro, and non-repro crashes.
- `TestManagerFailedBuild` and helper checks validate manager current build and failed kernel/syzkaller build bug state.
- `TestLinkifyReport` verifies source file/line references in reports are converted to repository links while escaping angle-bracket frames.

## Control flow and state behavior

The initialization path modifies process environment and global dashboard config before tests run. `testConfig` creates multiple namespaces with different access levels and reporting pipelines, so tests can verify cross-namespace isolation and access semantics. The core tests use dashboard clients to write datastore entities through real API handlers, then read bugs, managers, builds, crashes, and report state through test helpers.

Crash retention tests rely on repeated crash reports and mocked time advancement to trigger `purgeOldCrashes`. Manager failed-build tests transition from good builds to failed kernel and syzkaller builds, then back to good builds, verifying manager fields are reset only when the corresponding kernel or syzkaller commit changes. Linkification is a pure text transformation test but protects UI rendering of crash reports.

## Dependencies and integration points

This file depends on `dashapi`, `pkg/auth`, `pkg/subsystem`, subsystem list registration, `targets`, App Engine user APIs, and broad dashboard globals. Its config is used by `api_test.go`, `ai_test.go`, and `ai_report_test.go`, especially namespace `ains` with AI base repository settings and AI-capable clients.

## Risks and edge cases

Because `testConfig` is global and mutable through `transformContext`/`SetAIConfig`, tests must isolate contexts and avoid leaking config mutations. The `init` environment workaround is necessary to prevent metadata fetch hangs in local tests; removing it could make the whole package hang or panic. The large config can mask missing production config validation unless `checkConfig` stays strict. Crash purging is sensitive to reported crash preservation, repro-level buckets, manager/title uniqueness, and text blob deletion.

## Test signals

This file is both infrastructure and regression coverage. Passing tests signal that the dashboard can register handlers, authenticate clients, isolate namespaces, ingest builds/crashes, update reporting state, enforce access redirects/statuses, purge old crash data without deleting important reports, track failed builds, and linkify source locations correctly.
