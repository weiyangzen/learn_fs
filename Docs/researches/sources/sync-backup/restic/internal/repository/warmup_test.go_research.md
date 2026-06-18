
# sources/sync-backup/restic/internal/repository/warmup_test.go

Purpose: tests repository warmup delegation to backend warmup APIs.

The test backend records handles passed to `Warmup` and `WarmupWait`. Tests create pack ID sets, call `StartWarmup`, inspect `HandleCount`, and call `Wait` to verify the same backend handles are used. Scenarios include empty pack sets and non-empty sets.

State is mock backend call recording, not persisted repository data. Integration points include `Repository.StartWarmup`, backend `Warmup`, backend `WarmupWait`, and `restic.WarmupJob`. Risks covered include incorrect handle type/name construction, losing returned handles, and waiting on the wrong handle list.
