# sources/object-store/minio-mc/cmd/replicate-status.go

## Purpose
Implements `mc replicate status`, the bucket server-side replication status command. It gathers live replication metrics, remote target health, replication configuration, and optional per-node transfer rates, then renders either JSON or a detailed terminal table.

## Important APIs, types, and functions
- `replicateStatusFlags` defines `--backlog` and `--nodes`; only `--nodes` is used in this file.
- `replicateStatusCmd` registers the `status` subcommand under replication.
- `checkReplicateStatusSyntax` enforces exactly one `TARGET/BUCKET`.
- `replicateStatusMessage` is the default output payload, carrying `replication.MetricsV2`, remote targets, and the active `replication.Config`.
- `replicateXferMessage` is the `--nodes` output payload around `replication.ReplQueueStats`.
- `getNodeTheme` hashes node names with FNV to assign stable color themes.

## Control flow
`mainReplicateStatus` creates a cancelable context, configures console colors, validates syntax, constructs a regular client plus an admin client, fetches metrics with `GetReplicationMetrics`, fetches remote targets with `ListRemoteTargets`, and fetches replication configuration with `GetReplication`. If `--nodes` is set it prints `replicateXferMessage`; otherwise it prints `replicateStatusMessage`.

`replicateStatusMessage.String` normalizes stale ARN metrics away by comparing metric ARNs against current replication rules and role ARN. It then builds a table of target-specific replication counts, queue depth, transfer rate, target latency, link health, downtime, errors, and optional bandwidth limit state. Multi-target mode adds a summary section. `replicateXferMessage.String` renders node-level large and small object transfer rates and workers.

## State and persistence
The command does not persist local state. It reads remote MinIO server state: bucket replication metrics, remote target definitions, and replication config. Time-dependent fields include uptime, total/current downtime, latency, and queue stats.

## Dependencies and integration points
Integrates with MinIO client abstractions (`newClient`, `GetReplicationMetrics`, `GetReplication`), MinIO admin API (`newAdminClient`, `ListRemoteTargets`), `minio-go/pkg/replication`, `madmin-go/v3`, `console` color themes, `tablewriter`, and global output machinery via `printMsg`.

## Risks and edge cases
- Stale metric ARNs are filtered by rule destination or role ARN; a mismatch between config and metrics can hide historical data.
- `ListRemoteTargets` and `GetReplication` are fatal, so partial status cannot be displayed if one metadata call fails.
- Negative replicated counts and sizes are explicitly clamped after stale target subtraction.
- `--backlog` is declared but unused here, suggesting either implementation elsewhere or a stale flag.

## Test signals
No direct tests in this subset. Coverage would need command-level tests that mock client/admin APIs and formatter tests for stale ARN filtering, single-target vs multi-target output, and node transfer rendering.
