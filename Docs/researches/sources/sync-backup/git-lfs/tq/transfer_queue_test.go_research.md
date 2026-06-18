# sources/sync-backup/git-lfs/tq/transfer_queue_test.go

Purpose: tests retry counter defaults/backoff and transfer queue adapter switching behavior.

Important APIs/types/functions: tests for manifest retry defaults, `retryCounter`, `BatchSize`, and `useAdapter` reuse/switch cases.

Control flow: constructs retry counters and queues with simple manifests, invokes methods, and asserts counts, durations, and adapter identity/name.

State and persistence: queues start background goroutines, but tests do not enqueue real transfers or call full wait flows in shown cases.

Dependencies and integration points: uses `lfsapi.NewClient`, `NewManifest`, and `testify/assert`.

Risks: tests instantiate queues without exercising cleanup/wait in all cases, which can leave background goroutines in a larger test run if not handled by Go process exit. Does not cover retry integration with actual adapter results.

Test signals: good coverage for retry arithmetic and adapter normalization of empty name to basic.
