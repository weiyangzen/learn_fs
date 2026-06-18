# sources/storage-engines/tikv/src/server/gc_worker/mod.rs

## Purpose

This module file defines the public surface of `server::gc_worker`, wires submodules together, re-exports worker/config/compaction APIs, and provides the shared table-property `check_need_gc` helper used by range GC.

## Important APIs, Types, And Functions

- Public modules: `compaction_filter` and `rawkv_compaction_filter`.
- Private modules: `compaction_runner`, `config`, `gc_manager`, and `gc_worker`.
- Re-exports include `WriteCompactionFilterFactory`, `CompactionCandidate`, `CompactionRunner`, `CompactionRunnerHandle`, `AutoCompactionConfig`, `GcConfig`, `GcWorkerConfigManager`, `AutoGcConfig`, `GcSafePointProvider`, `GcTask`, `GcWorker`, `STAT_RAW_KEYMODE`, `STAT_TXN_KEYMODE`, `sync_gc`, and `RawCompactionFilterFactory`.
- Test/failpoint exports include `TestGcRunner`, `gc_by_compact`, `FIRST_COMPACTION_CANDIDATE_REGION`, `MockSafePointProvider`, and `PrefixedEngine`.
- It re-exports `Callback`, `Error`, `ErrorInner`, and `Result` from storage pending a dedicated GC worker error type.
- `check_need_gc` is the module-level heuristic for deciding whether MVCC properties justify GC.

## Control Flow

The only functional control flow is `check_need_gc`: negative or infinite ratio threshold disables GC; threshold below 1.0 forces GC; if `props.min_ts` is above the safe point it skips; otherwise it triggers when versions exceed rows times threshold or versions exceed puts times threshold. It is deliberately an optimization and can be false positive because table properties are file-based.

## State And Persistence Behavior

The module file has no persistent state. It determines visibility and centralizes a stateless GC heuristic.

## Dependencies And Integration Points

It depends on `engine_traits::MvccProperties`, `txn_types::TimeStamp`, sibling modules, raw KV compaction filtering, and storage-level callback/error types. Its re-exports are the integration point used by the broader server and storage code to start GC workers, install compaction filters, schedule synchronous GC, and configure automatic compaction.

## Risks

- Re-exporting storage `Error` and `Result` couples GC worker API to storage errors; the TODO notes this should become a separate error type.
- `check_need_gc` is heuristic and can cause extra scans or skip work until later compaction/property changes.
- Public/private module boundaries are important: `compaction_runner` is private but selected types are public, so new APIs must be intentionally re-exported.

## Test Signals

Tests validate `check_need_gc` edge cases for disabled/forced thresholds and real RocksDB MVCC properties. The property test verifies transitions from no-GC, to GC after deleted multi-version keys, to no-GC after manual cleanup, and GC for a single lock version.
