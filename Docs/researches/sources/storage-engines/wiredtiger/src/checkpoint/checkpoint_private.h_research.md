# sources/storage-engines/wiredtiger/src/checkpoint/checkpoint_private.h

## Purpose

Defines checkpoint-private constants, lifecycle-state enum, stats structs, progress structs, server-thread state, timer state, and private prototypes used by checkpoint implementation files. It is included by `checkpoint.h` but keeps details scoped to checkpoint internals.

## Important APIs, Types, And Functions

`WTI_CHECKPOINT_SESSION_FLAGS` describes internal checkpoint session capabilities. `WTI_CKPT_FOREACH_NAME_OR_ORDER` iterates checkpoint arrays that may contain unnamed but ordered entries. `WTI_CHECKPOINT_STATE` enumerates phase/progress states from inactive through metadata, btree, oldest update, sync/evict/block-manager, history-store, commit, rollback/log/tree/establish/start-transaction phases.

`WTI_CKPT_HANDLE_STATS` accumulates handle apply/drop/lock/meta-check/skip counts and durations. `WTI_CKPT_PROGRESS` tracks files checkpointed, progress message count, pages visited, write bytes, and write pages. `WTI_CKPT_THREAD` stores the checkpoint server's condition variable, session, thread id, log-size threshold, signal state, and wait interval; `WT_CKPT_LOGSIZE` reads its atomic log-size field. `WTI_CKPT_TIMER` stores min/max/recent/total timing. Private prototypes expose parallel checkpoint worker commit and snapshot-release helpers.

## Control Flow

The header has no executable flow, but its enum ordering mirrors checkpoint lifecycle sequencing for progress/state reporting. The private iterator controls cleanup flow in `checkpoint_ckptlist.c`. `WT_CKPT_LOGSIZE` controls whether log-size checkpoint signaling is active. The private parallel prototypes are called from checkpoint transaction code after queued reconciliation work is complete.

## State And Persistence Behavior

All definitions are runtime state except where they describe phases of producing durable checkpoint metadata. Handle stats, progress counters, timers, log-size signal state, and lifecycle enum values are transient observability and scheduling state. The iterator macro affects memory cleanup of checkpoint metadata descriptors that represent persistent checkpoint records.

## Dependencies And Integration Points

Consumed by `checkpoint.h`, checkpoint server code, checkpoint stats code, checkpoint transaction code, parallel reconciliation code, and checkpoint-list cleanup. The enum and stats fields must stay aligned with connection statistics and verbose/progress reporting. The prototypes form private cross-file links not intended for broader subsystems.

## Risks

Changing enum order can confuse progress/state consumers that assume lifecycle ordering. Timer minima are initialized to `UINT64_MAX` elsewhere; stats publication must preserve that convention. The private iterator's stop condition differs from public checkpoint iteration and is required to avoid leaks. Atomic log-size access must remain compatible with signal paths.

## Test Signals

Signals include compilation/prototype generation, checkpoint progress/verbose tests that observe expected state transitions, stats tests for handle/timer counters, log-size checkpoint scheduling tests through `WT_CKPT_LOGSIZE`, and checkpoint-list cleanup tests with ordered unnamed checkpoints.
