# sources/object-store/minio/cmd/data-scanner-metric.go

## Purpose
`data-scanner-metric.go` records scanner operation counters, last-minute latency windows, ILM action metrics, active disk paths, current cycle info, and admin-reportable scanner metrics.

## Important APIs, Types, And Functions
`scannerMetric` enumerates realtime and trace-only scanner operations. `scannerMetrics` stores atomic operation counters, locked latency accumulators, lifecycle action counters, current path trackers, and cycle info. Timing helpers include `log`, `timeN`, `time`, `timeSize`, `incTime`, and `timeILM`. `currentPathUpdater`, `getCurrentPaths`, and `activeDrives` expose active scan locations. `setCycle`, `getCycle`, and `report` publish cycle/admin metrics.

## Control Flow
Scanner code wraps operations with returned closures that add counters/latencies when invoked. Trace-only metrics publish scanner traces only when subscribers exist. Current paths are stored per disk in `sync.Map`, with the current string pointer updated atomically. Reports snapshot counters and last-minute windows into `madmin.ScannerMetrics`.

## State And Persistence Behavior
All state is in memory and process-local. Counters are lifetime since process start; cycle completion history is copied from the persisted scanner cycle state but not persisted here.

## Dependencies And Integration Points
It integrates with `data-scanner.go`, lifecycle actions, madmin scanner metrics, global scanner tracing, last-minute latency accumulator types, and `globalLocalNodeName`.

## Risks And Test Signals
The unsafe pointer current-path tracker is intentionally lightweight but relies on careful atomic pointer use. Metrics can be approximate under concurrency. No direct tests are in this subset; scanner tests indirectly exercise ILM paths but not metric reporting.
