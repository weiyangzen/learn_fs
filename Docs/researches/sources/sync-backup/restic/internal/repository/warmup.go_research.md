
# sources/sync-backup/restic/internal/repository/warmup.go

Purpose: exposes repository-level cold-storage warmup for pack files.

`warmupJob` implements `restic.WarmupJob` with `HandleCount` and `Wait`. `Repository.StartWarmup` converts a set of pack IDs to backend pack handles, calls `Backend.Warmup`, and returns a job containing only the handles still warming up. `Wait` delegates to `Backend.WarmupWait`.

State is backend-managed warmup state; the repository stores only the handles returned by the backend. Integration points include `CopyBlobs` when the S3 restore feature flag is enabled and any backend implementing cold storage restore. Risks include backend-specific semantics, unordered ID sets, context cancellation during warmup wait, and ensuring callers handle zero-handle jobs without unnecessary waits. Tests in `warmup_test.go` validate handle conversion and wait delegation.
