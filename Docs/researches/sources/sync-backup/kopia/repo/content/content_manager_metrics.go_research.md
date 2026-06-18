# sources/sync-backup/kopia/repo/content/content_manager_metrics.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_manager_metrics.go_research.md`.

Purpose: defines the content manager metric counters and throughput measurements used by write, read, compression, encryption, hashing, dedupe, and upload paths.

Important APIs and types: `metricsStruct` groups metric handles. `initMetricsStruct` registers counters such as `content_uploaded_bytes`, `content_get_error_count`, `content_get_not_found_count`, `content_deduplicated`, `content_deduplicated_bytes`, compression byte counters, and throughput metrics for write, hash, encryption, read, decryption, decompression, and compression attempts.

Control flow and integration: this file has no runtime branching beyond construction. The returned struct is embedded in shared manager state and used by functions in `content_manager.go` and `content_manager_lock_free.go`: `WriteContent` observes pre-dedupe write throughput, `hashData` observes hashing, compression/encryption helpers update compression and encryption counters, `GetContent` reports success/not-found/error, and pack/index upload paths increment uploaded bytes.

State and persistence behavior: metrics are process-local telemetry, not repository state. They should not affect behavior or durability.

Dependencies: `internal/metrics.Registry`.

Risks and test signals: metric names are integration contracts for monitoring. Renaming or changing units can break dashboards. The code is indirectly covered through content manager tests that exercise all paths, but there are no dedicated metric assertions in this source set.
