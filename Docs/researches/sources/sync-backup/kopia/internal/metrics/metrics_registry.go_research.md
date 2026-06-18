# sources/sync-backup/kopia/internal/metrics/metrics_registry.go

Purpose: owns metric instances, captures snapshots, logs metrics, and tracks registry lifetime for leak detection.

Important APIs/types/functions: `Registry`, `Snapshot`, `Snapshot.mergeFrom`, `createSnapshot`, `Registry.Snapshot`, `Close`, `Log`, `NewRegistry`, and `labelsSuffix`.

Control flow: `NewRegistry` initializes metric maps and records creation with `releasable`. `Snapshot` collects every counter and distribution, then locks registry metadata to set start/end times and optionally reset the registry start time. `Log` emits counters and non-empty distributions. `Close` is nil-safe and marks the registry released.

State/persistence behavior: registry state is in-memory; snapshots are serializable and carry start/end/user/host plus metric maps. Snapshot reset clears local metric states but does not remove metric objects or reset Prometheus exporters.

Dependencies/integration: depends on `internal/clock`, `internal/releasable`, and repository logging. Other metric files attach counters, throughput, and distributions to this registry.

Risks/test signals: `Snapshot` iterates metric maps without holding `r.mu`, so concurrent metric registration could race with snapshotting. `labelsSuffix` iterates maps without sorting, which can make full names unstable for multi-label maps.
