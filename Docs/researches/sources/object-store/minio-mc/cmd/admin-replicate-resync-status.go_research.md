# sources/object-store/minio-mc/cmd/admin-replicate-resync-status.go

## Purpose
Implements `mc admin replicate resync status`, showing real-time resync metrics for a replicated peer site.

## Important APIs, types, and functions
Important symbols include `adminReplicateResyncStatusCmd`, `mainAdminReplicationResyncStatus`, `initResyncMetricsUI`, `resyncMetricsUI`, and its Bubble Tea `Init`, `Update`, and `View` methods.

## Control flow
The handler validates source and peer aliases, fetches site replication info, resolves the peer by deployment ID, starts a cancelable metrics stream filtered with `madmin.MetricsSiteResync` and `ByDepID`, and either prints JSON metrics or sends `SiteResyncMetrics` into an interactive Bubble Tea UI until complete, canceled, or interrupted.

## State and persistence behavior
The command is read-only against server resync state. Local UI state stores the current metrics snapshot, spinner, quitting flag, and peer deployment ID.

## Dependencies and integration points
It integrates MinIO realtime metrics APIs, `metricsMessage` from scanner status for JSON output, Bubble Tea, bubbles spinner, lipgloss styles, tablewriter, humanized byte rates, global context, and peer resolution from replication info.

## Risks and edge cases
The disabled-replication branch colorizes a string but does not print it. Versions display uses `ReplicatedCount`, which may be intentional or a bug if versions differ. UI and metrics goroutine coordination relies on context cancellation.

## Test signals
Tests should cover peer lookup, disabled replication behavior, JSON streaming, UI update on complete/canceled metrics, ctrl-c handling, throughput calculation with elapsed time, and non-canceled metrics errors.
