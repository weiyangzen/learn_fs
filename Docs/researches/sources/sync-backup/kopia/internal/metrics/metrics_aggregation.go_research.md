# sources/sync-backup/kopia/internal/metrics/metrics_aggregation.go

Purpose: aggregates multiple metric snapshots into one combined snapshot.

Important APIs/types/functions: `AggregateSnapshots`, `Snapshot`, `createSnapshot`, and `Snapshot.mergeFrom`.

Control flow: `AggregateSnapshots` initializes an empty snapshot and calls `mergeFrom` for each input. Counters are summed, and distribution states merge count, sum, min/max, and buckets via `mergeFrom`.

State/persistence behavior: returns a new in-memory snapshot. It does not currently set aggregate start/end/user/host fields, so callers should treat it as value aggregation rather than a full identity-preserving snapshot.

Dependencies/integration: relies on registry snapshot structures in `metrics_registry.go` and distribution merge behavior in `metrics_distribution.go`.

Risks/test signals: aggregate behavior assumes compatible bucket layouts for distributions with the same name. If bucket counts differ, `mergeScaledFrom` skips bucket merging after initializing state, potentially losing bucket details.
