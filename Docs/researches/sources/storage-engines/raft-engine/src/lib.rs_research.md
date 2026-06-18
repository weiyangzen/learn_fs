# sources/storage-engines/raft-engine/src/lib.rs

## Purpose
`lib.rs` is the crate root for raft-engine. It declares feature gates and modules, defines core public exports, provides a crate-wide boxed-error macro, tracks global entry statistics, and enforces the internal-key namespace used by atomic group metadata.

## Important APIs, Types, And Functions
`box_err!` formats a boxed error with source file and line. Public exports include `Config`, `RecoveryMode`, `Engine`, `Error`, `Result`, `Command`, `LogBatch`, `MessageExt`, performance-context helpers, `Version`, and `ReadableSize`. `env` is public, while most implementation modules are private.

The `internals` feature exposes selected internal modules for advanced users or tests: event listeners, file pipe log internals, memtable, pipe log, purge, optional swap allocator, and write barrier.

`GlobalStats` holds relaxed atomics for live append entries, rewrite entries, and deleted rewrite entries. `add`, `delete`, `rewrite_entries`, `deleted_rewrite_entries`, `reset_rewrite_counters`, `live_entries`, and `flush_metrics` update and report logical entry counts by queue.

`INTERNAL_KEY_PREFIX`, `make_internal_key`, and `is_internal_key` reserve internal keyspace. In non-test builds, only the atomic group key is recognized when checking the prefix without an explicit extension; in tests, any prefixed key can be treated as internal to validate broader behavior.

## Control Flow
The crate root mostly configures compile-time structure. Runtime calls to `GlobalStats` increment append or rewrite counters when entries are added and decrement or mark deleted when entries are removed. `live_entries` computes rewrite live count as total rewrite entries minus deleted rewrite entries with saturating subtraction, and `flush_metrics` publishes both queue counts.

Internal keys are created by prefixing an extension with `b"__"`. User-facing `LogBatch::put` and `put_message` reject such keys, while internal code uses unchecked insertion for atomic group markers. Replay paths filter internal keys so they do not become user-visible.

## State And Persistence Behavior
`GlobalStats` is in-memory observability state only. Internal keys are persisted as ordinary key-value log items but use a reserved prefix and are filtered from user state. The comments explicitly note that this protects current and future internal keys from being visible after downgrade as long as old versions also respect the prefix.

## Dependencies And Integration Points
`lib.rs` ties all major modules together: config, consistency, engine, errors, event listeners, file pipe log, optional filter, fork, log batch, memtable, metrics, pipe log, purge, utility code, and write barrier. `LogBatch` depends on `make_internal_key` and `is_internal_key` for atomic groups; metrics code depends on `GlobalStats::flush_metrics`.

## Risks And Edge Cases
The relaxed atomic counters are appropriate for metrics but not for synchronization. `reset_rewrite_counters` subtracts the current deleted count from both rewrite counters and assumes concurrent use tolerates approximate accounting. Non-test `is_internal_key(s, None)` only checks the atomic group extension, so adding future internal keys requires updating this function. `box_err!` embeds file and line, which is useful diagnostically but can make exact error strings unstable.

## Test Signals
The test module initializes env logging, implements `MessageExt` for raft `Entry`, and verifies internal-key matching with and without explicit extensions. Many crate-wide tests depend on that `MessageExt` implementation when encoding raft entries into `LogBatch`.
