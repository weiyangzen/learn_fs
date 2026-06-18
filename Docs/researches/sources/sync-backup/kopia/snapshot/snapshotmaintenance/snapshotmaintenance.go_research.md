# sources/sync-backup/kopia/snapshot/snapshotmaintenance/snapshotmaintenance.go

Purpose: orchestrates snapshot GC plus low-level repository maintenance for writable repositories.

Important APIs/types/functions: `ErrReadonly` and `Run`.

Control flow: `Run` rejects read-only repository connections, enables the repository log manager, and invokes `maintenance.RunExclusive`. For full maintenance it runs `snapshotgc.Run` with deletion enabled before calling generic `maintenance.Run`; auto/quick modes skip snapshot GC unless maintenance scheduling chooses full mode.

State and persistence: can mutate repository maintenance metadata, logs, content indexes, content deletion state, and snapshot GC state through delegated maintenance tasks.

Dependencies and integration points: used by CLI/server maintenance entry points. Integrates `repo.DirectRepositoryWriter`, `maintenance.Mode`, `maintenance.SafetyParameters`, and `snapshotgc`.

Risks and test signals: read-only protection is the only guard in this wrapper; exclusive maintenance handles concurrency. Snapshot GC failures abort full maintenance. Tests assert read-only error and full maintenance behavior across repository format versions.
