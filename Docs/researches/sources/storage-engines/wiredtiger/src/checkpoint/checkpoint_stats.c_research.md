# sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_stats.c

## Purpose

Publishes and maintains checkpoint-related connection statistics for handle processing, timers, reconciliation/sync ratio, and apply-versus-skip decisions. It bridges runtime fields in `WT_CKPT_CONNECTION` to stat counters visible to diagnostics and users.

## Important APIs, Types, And Functions

`__wt_checkpoint_handle_stats_clear` resets handle count/time accumulators. `__wt_checkpoint_timer_stats_clear` initializes timer minima for checkpoint API, prepare, and scrub timers. `__wt_checkpoint_handle_stats` writes handle-related stats to the connection stats array. `__wt_checkpoint_rec_time_stats` atomically accumulates per-file reconciliation and sync ticks. `__wt_checkpoint_timer_stats` publishes scrub, prepare, and overall checkpoint timer max/min/recent/total values and computes reconciliation percentage of sync time. `__wt_checkpoint_apply_or_skip_handle_stats` increments apply or skip counters based on `WT_BTREE_SKIP_CKPT`.

## Control Flow

Clear functions operate directly on `S2C(session)->ckpt`. Handle stat publication copies accumulated values plus the externally measured handle-gather duration. Reconciliation time stats use atomic adds because multiple file or helper paths can contribute. Timer publication reads timer fields atomically, publishes min only after it has been set away from `UINT64_MAX`, and computes `checkpoint_sync_rec_pct` as `reconcile_ticks * 100 / sync_ticks` when sync ticks are nonzero. Apply-or-skip checks the current btree flag and updates the corresponding count and duration.

## State And Persistence Behavior

This file does not affect persistent checkpoint contents. It maintains transient observability state for the current or recent checkpoint activity. The stats reflect handle selection and reconciliation behavior, which helps diagnose durable checkpoint latency and skipped files but is not itself stored in metadata.

## Dependencies And Integration Points

Depends on `WT_CKPT_CONNECTION` from `checkpoint.h`, private handle/timer structs from `checkpoint_private.h`, connection stat macros, atomic operations, and btree flags. It is called from checkpoint transaction and btree sync paths that measure handle gathering, per-file reconciliation/sync, checkpoint preparation, and skip/apply behavior.

## Risks

Stats can be updated from multiple paths, so non-atomic fields must only be touched in serialized checkpoint phases while shared accumulators use atomics. Timer minima require `UINT64_MAX` initialization or min publication becomes misleading. Percentage computation can overflow if reconciliation ticks are extremely large before multiplication, though normal clock deltas make that unlikely. Apply/skip stats depend on `S2BT(session)` being the handle currently evaluated.

## Test Signals

Signals include statistics tests that run checkpoints over applied and skipped handles, verify handle count/duration fields, verify timer min/max/recent/total after checkpoints, and check `checkpoint_sync_rec_pct` after reconciliation. Parallel checkpoint tests should still produce coherent aggregate reconciliation time. Diagnostics should include skipped btree handles marked with `WT_BTREE_SKIP_CKPT`.
