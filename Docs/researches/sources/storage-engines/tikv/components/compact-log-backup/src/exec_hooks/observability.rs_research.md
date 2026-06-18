# sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/observability.rs

Purpose: provides the default TTY/operator-facing `ExecHooks` implementation for compact-log-backup progress, metrics, abort logging, and async backtrace dumping.

Important APIs and types: `Observability { stats, meta_len }` implements `ExecHooks`. It consumes `BeforeStartCtx`, `SubcompactionStartCtx`, `SubcompactionFinishCtx`, `AfterFinishCtx`, and `AbortedCtx`.

Control flow: before execution it initializes `tracing_active_tree`, spawns a SIGUSR1 handler that writes `/tmp/compact-sst.dump`, records total metadata object count, and logs config and storage URL. Before each subcompaction it accumulates metadata/collector deltas and logs region, CF, time range, input count, and size. After each subcompaction it aggregates result stats, observes Prometheus histograms, computes a rough logical-byte throughput, and logs global progress. On finish it rejects empty non-sharded runs but allows empty shard matches.

State and persistence: in-memory stats only, plus optional `/tmp/compact-sst.dump` written on SIGUSR1. Prometheus histograms are process-global.

Dependencies and integration: integrates with `statistic::prom`, `storage_url`, Tokio Unix signals, TiKV logging macros, and the execution hook lifecycle.

Risks: `SignalKind::user_defined1()` and Unix signal support are platform-specific. Throughput divides by elapsed milliseconds; extremely fast compactions can produce inf/nan-like values. The empty-input policy is intentionally asymmetric for sharded vs unsharded compactions.

Test signals: indirectly covered by execution tests that rely on hook lifecycle; empty-input behavior is a likely area for targeted tests.
