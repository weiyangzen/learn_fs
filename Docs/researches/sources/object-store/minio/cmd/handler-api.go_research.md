<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/handler-api.go -->
# sources/object-store/minio/cmd/handler-api.go

## Purpose
Stores runtime API configuration and request throttling behavior for S3 handlers. It calculates request concurrency from configuration or memory limits, exposes thread-safe getters, and implements `maxClients` admission control.

## Important APIs, types, and functions
- `apiConfig` holds request pool, cluster deadline, list quorum, CORS origins, replication/transition worker settings, cleanup intervals, O_DIRECT/gzip/root/sync-events flags, and object version cap.
- `cgroupMemLimit` and `availableMemory` derive memory budgets from cgroup or host memory.
- `(*apiConfig).init` applies `api.Config` to runtime state and resizes workers/request pool.
- Getter methods expose immutable copies or defaults under `RWMutex`.
- `maxClients` enforces request pool capacity and service-freeze behavior.
- `getReplicationOpts`, `getTransitionWorkers`, `isSyncEventsEnabled`, and `getObjectMaxVersions` feed background subsystems.

## Control flow
Initialization chooses cluster deadline and CORS defaults, calculates per-node max requests from configured limit or memory divided by estimated per-request erasure memory, replaces the request pool only when capacity changes, resizes replication and transition workers, updates cleanup intervals, and signals stale-upload cleanup goroutines when the interval changes. `maxClients` increments incoming/queued stats, optionally waits for service unfreeze, emits rate-limit headers, admits if it can send into the pool, returns 499 on client cancellation, or returns `ErrTooManyRequests` if full.

## State and persistence behavior
State is in-memory runtime configuration guarded by a mutex. It affects cleanup timers, request concurrency, metrics, and background worker counts but does not persist configuration itself.

## Dependencies and integration points
Depends on MinIO API config, global server memory limit, erasure block sizes, replication pool, transition state, HTTP stats, service-freeze global, context trace metadata, and stale upload cleanup channel in `erasure-sets.go`.

## Risks and edge cases
Concurrency resizing leaves a short overlap where existing requests use the old pool. Request limits based on memory estimates can be too high or low for unusual layouts. `maxClients` uses non-blocking admission and can reject bursts immediately. Correct 499 auditing depends on response recorder behavior after cancellation.

## Test signals
No direct tests in this group. Signals include request throttling integration tests, rate-limit headers, busy/too-many-request responses, cleanup interval changes, and worker pool resizing behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/handler-api.go -->
