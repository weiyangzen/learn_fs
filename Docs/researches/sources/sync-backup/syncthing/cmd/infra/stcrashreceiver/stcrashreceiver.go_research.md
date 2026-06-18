# sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/stcrashreceiver.go

Purpose: HTTP handler for crash report storage, retrieval, existence checks, filtering, metrics, and Sentry queueing.

Important APIs/types/functions: `crashReceiver` holds `diskStore`, `sentryService`, and optional `ignorePatterns`. Methods are `ServeHTTP`, `serveGet`, `serveHead`, and `servePut`.

Control flow: `ServeHTTP` extracts the final path component, lowercases it, validates it is exactly 64 hex characters, then dispatches GET, HEAD, PUT, or 405. GET returns the uncompressed stored report. HEAD checks existence. PUT reads up to 1 MiB, records first line for logs, applies ignore patterns, stores report asynchronously, sends it to Sentry asynchronously, logs receipt, and increments crash report metrics with the final result.

State and persistence behavior: PUT persists compressed reports through diskStore and enqueues Sentry processing. GET reads persisted reports. Metrics counters capture receive, ignored, queue, and sentry failures.

Dependencies/integration: main mux mounts this handler at `/`; it depends on diskstore, sentry service, ignore matching, `userIDFor`, and standard HTTP semantics.

Risks/test signals: truncated oversized bodies can still be accepted. If disk queue succeeds but Sentry queue fails, result becomes `sentry_failure` even though report was stored. Signal is correct status codes for bad IDs/methods, successful PUT/HEAD/GET round trip, and metrics labels reflecting outcomes.
