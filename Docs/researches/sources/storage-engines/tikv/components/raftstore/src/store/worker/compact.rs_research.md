# sources/storage-engines/tikv/components/raftstore/src/store/worker/compact.rs

## Purpose
This worker runs manual RocksDB compactions for raftstore. It supports explicit CF range compaction and experimental periodic full-store compaction split into ranges with load-sensitive pauses.

## Important APIs, Types, and Functions
- `Task::Compact { cf_name, start_key, end_key, bottommost_level_force }` compacts a CF range.
- `Task::PeriodicFullCompact { ranges, compact_load_controller }` launches asynchronous full compaction over provided ranges or the whole store.
- `FullCompactController` contains pause backoff settings and an `incremental_compaction_pred` predicate.
- `FullCompactController::pause` waits on `GLOBAL_TIMER_HANDLE` with exponential-style retry until the predicate allows progress.
- `Runner<E>` owns a `KvEngine` clone and a YATP `Remote`.
- `full_compact` performs incremental compaction and observes full/increment/pause metrics.
- `compact_range_cf` performs synchronous CF range compaction.
- `FULL_COMPACTION_IN_PROCESS` prevents concurrent periodic full compactions.

## Control Flow
For `Compact`, the runner starts the `COMPACT_RANGE_CF` timer, builds `ManualCompactionOptions` with bottommost-level forcing as requested, calls `engine.compact_range_cf`, logs success or failure, and observes duration.

For `PeriodicFullCompact`, the runner atomically checks and sets `FULL_COMPACTION_IN_PROCESS`. If another full compaction is active, it logs and returns. Otherwise it clones the engine and spawns an async task on the future pool. The async task converts ranges into optional start/end slices, inserts a whole-store `(None, None)` range when no ranges are provided, compacts each increment with `compact_range`, and before moving to the next increment pauses when the predicate is false. Completion or failure clears the global in-process flag.

## State and Persistence Behavior
Compaction mutates RocksDB storage layout and can remove obsolete versions/tombstones, but it does not change logical KV contents or raft metadata. Full compaction uses `ManualCompactionOptions::new(false, 1, false)`, while range compaction can force bottommost compaction. The only local process state is the global atomic in-process flag and metrics.

## Dependencies and Integration Points
The worker depends on `engine_traits::{KvEngine, ManualCompactionOptions}`, YATP futures, `GLOBAL_TIMER_HANDLE`, failpoints, and Prometheus metrics from `worker::metrics`. It is exported through `worker/mod.rs` and wrapped by `cleanup.rs`.

## Risks and Edge Cases
`FullCompactController::pause` updates `duration_secs` with `max(max_pause, duration * 2)`, which jumps to at least the configured max after a failed predicate rather than capping at max; that may be intentional or a subtle backoff issue. If the spawned async task panics before clearing `FULL_COMPACTION_IN_PROCESS`, future full compactions could be suppressed. Full compaction is explicitly experimental and has a TODO for stopping/cancellation. Manual compaction can be disabled at the engine level, in which case compaction may not reduce SST size.

## Test Signals
Tests verify disabling/enabling manual compaction affects SST size, explicit compact-range reduces duplicated SST data, full compaction removes delete/tombstone overhead in MVCC write CF, and incremental full compaction can pause until the predicate becomes true.
