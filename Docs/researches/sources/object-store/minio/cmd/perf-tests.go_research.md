# sources/object-store/minio/cmd/perf-tests.go

## Purpose
This file implements object, drive, and network performance measurement helpers used by MinIO admin support tooling and peer REST endpoints.

## Important APIs, Types, and Functions
`SpeedTestResult` records upload/download bytes, timings, TTFB, and errors. `selfSpeedTest` performs concurrent PUTs then GETs using the MinIO client and records durations. `netPerfRX` tracks received bytes between connection timing boundaries. `netperf` streams random data to peer `DevNull` endpoints. `siteNetperf` performs similar cross-site traffic through replication admin clients. `perfNetRequest` builds and executes site netperf HTTP requests.

## Control Flow and State
`selfSpeedTest` runs uploads for `opts.duration`, then downloads created objects for another duration. It cancels all workers on first real error and bypasses API freeze with performance metadata. Network tests use a shared random reader and close an EOF channel after duration, then compute TX/RX rates from atomic counters and RX sampling windows.

## Dependencies and Integration Points
The file depends on global MinIO clients, IAM/root access config, site replication system, peer clients, `DevNull` handlers, admin transports, and madmin result types.

## Risks and Test Signals
Perf tests intentionally create load and objects under a speed-test prefix, so cleanup expectations matter outside this file. Shared reader concurrency and first-error strings can race semantically even though counters are atomic. RX calculations depend on connection timing; disconnections produce zero/error results. No direct tests in this subset.
