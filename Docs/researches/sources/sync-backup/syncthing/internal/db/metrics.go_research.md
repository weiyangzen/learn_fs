# sources/sync-backup/syncthing/internal/db/metrics.go

## Purpose
This file provides a Prometheus instrumentation wrapper for the `DB` interface, measuring current operations, total operation time, operation counts, and number of updated files.

## Important APIs, Control Flow, And State
`MetricsWrap(db DB) DB` returns `metricsDB`, which embeds the wrapped database. `account(folder, op)` increments `syncthing_db_operations_current`, records a start time, and returns a deferred closure that adds elapsed seconds, increments total operation count, and decrements current operations. Most `DB` and `KV` methods are overridden to defer `account` and delegate to `m.DB`. `Update` also adds `len(fs)` to `syncthing_db_files_updated_total`.

## Dependencies And Integration Points
It depends on Prometheus `promauto`, `config.PullOrder`, protocol types, and the local `DB` contract. It should wrap concrete databases close to construction so all consumers report consistent metrics.

## Risks And Test Signals
Iterator-returning methods measure only iterator creation, not full iteration duration. This is important when interpreting metrics for large scans. The `Update` method uses `defer metricTotalFilesUpdatedCount.WithLabelValues(folder).Add(...)`; the metric increments after the update returns regardless of success, because the defer is registered before the delegate call. Tests should confirm wrapper delegation, labels, and whether failed updates should count as updated-file attempts.
