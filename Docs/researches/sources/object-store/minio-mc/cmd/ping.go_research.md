# Research: sources/object-store/minio-mc/cmd/ping.go

## sources/object-store/minio-mc/cmd/ping.go

Purpose: implements `mc ping`, repeatedly checking MinIO liveness through anonymous admin APIs, optionally across distributed nodes, with summary statistics and signal-aware shutdown.

Important APIs and types: `pingCmd`, `PingResult`, `PingSummary`, `EndPointStats`, `ServerStats`, templates `Ping`/`PingDist`, helpers `fetchAdminInfo`, `filterAdminInfo`, `ping`, `pingStats`, `trimToTwoDecimal`, `pad`, `watchSignals`, and `mainPing`.

Control flow: `mainPing` validates args, builds admin and anonymous clients, optionally fetches server info for distributed/node mode, disables the global signal trap, installs its own summary-printing signal handler, and runs either a fixed-count loop or an infinite loop. Each `ping` call consumes `anonClient.Alive`, updates per-endpoint stats, prints a result, and sleeps by interval unless stopping.

State and persistence: no storage mutation. Maintains package-global `stop`, signal handlers, and a mutable summary map.

Dependencies and integration: uses `madmin` anonymous/admin clients, Go templates/tabwriter, shared `printMsg`, global context/cancel, and profiling shutdown.

Risks and tests: `stop` is package-global and not reset in `mainPing`, which can leak across repeated in-process invocations. `fetchAdminInfo` retries indefinitely until global cancellation. No direct tests exist.

<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/ping.go -->
