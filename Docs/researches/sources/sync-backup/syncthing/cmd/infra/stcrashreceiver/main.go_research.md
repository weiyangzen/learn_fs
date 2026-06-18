# sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/main.go

Purpose: entrypoint and failure-report handling for the Syncthing crash receiver HTTP service. It accepts crash report storage/check requests and, when configured with Sentry DSN, failure report uploads.

Important APIs/types/functions: `cli` config parsed by Kong; `maxRequestSize`; `main`; `handleFailureFn`; `saveFailureWithGoroutines`; `ignorePatterns`, `loadIgnorePatterns`, and `match`. CLI/env settings cover report dir, Sentry DSN, listen addresses, disk and Sentry queue sizes, disk retention limits, and ignore-pattern file.

Control flow: `main` creates disk and Sentry services, loads ignore regexes, wires `crashReceiver` at `/`, `/ping`, optional `/metrics` and pprof, and optional `/newcrash/failure`. Failure handler reads up to 1 MiB, applies ignore patterns, decodes `contract.FailureReport` JSON, parses version, builds Sentry packets, optionally stores goroutine data compressed, fingerprints sanitized message, and sends reports.

State and persistence behavior: persists crash reports under `crash_reports` and failure goroutine dumps under `failure_reports`; exposes metrics; caches Sentry clients elsewhere.

Dependencies/integration: integrates with Kong, raven-go, Prometheus, Syncthing build/version parsing, usage-report contracts, diskStore, sentryService, and ignore regex files.

Risks/test signals: `io.LimitReader` does not explicitly reject over-1MiB bodies, it truncates. `saveFailureWithGoroutines` writes without ensuring parent directories, depending on caller path layout. Signals are `/ping`, metrics, successful crash PUT/HEAD/GET, failure JSON reaching Sentry, and ignore counters incrementing.
