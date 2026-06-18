# sources/storage-engines/wiredtiger/src/include/rollback_to_stable.h

## Purpose
Defines rollback-to-stable (RTS) verbose tags, statistics helpers, phase identifiers, worker queue units, singleton RTS state, and session-walk callback state.

## Important APIs, Types, And Functions
- `WT_RTS_VERB_TAG_*` constants label fine-grained RTS verbose messages.
- `WT_CHECK_RECOVERY_FLAG_TXNID` checks whether a transaction id belongs to the recovery checkpoint snapshot range.
- `WT_VERB_RECOVERY_RTS` selects recovery+RTS verbose categories during recovery or RTS alone otherwise.
- `WT_RTS_STAT_CONN_INCR` and `WT_RTS_STAT_CONN_DATA_INCR` increment live or dry-run statistic variants.
- `WT_RTS_PHASE_*` constants identify progress phases.
- `WT_RTS_MAX_WORKERS` caps RTS workers.
- `struct __wt_rts_work_unit` stores queued URI rollback work.
- `struct __wt_rollback_to_stable` stores RTS methods, thread group, worker counts, spin-protected queue, dry-run flag, and progress counters/timers.
- `struct __wt_rts_cookie` returns active transaction/cursor findings from session walks.

## Control Flow
The header is mostly declarative. Stat macros branch on `S2C(session)->rts->dryrun`. Recovery verbose category selection branches on `WT_CONN_RECOVERING`. Work units are queued through a TAILQ protected by `rts_lock`; worker execution is implemented elsewhere through the method pointers and thread group.

## State And Persistence Behavior
RTS itself mutates persistent table/history-store state to roll data back to stable timestamps, but this header defines the connection-level runtime state and progress accounting. Dry-run mode redirects stats without applying live stat increments. Progress fields are shared and updated across RTS worker threads.

## Dependencies And Integration Points
Depends on connection flags, verbose categories, stats macros, TAILQ, spinlocks, thread groups, timestamps, timers, and session walk logic. Integrated with recovery, history store, btree rollback, metadata scanning, and shutdown RTS.

## Risks
RTS is correctness-critical for timestamp recovery. Dry-run branching must mirror real stats. Shared progress counters need atomic/safe access. Queue locking must protect work-unit membership. Verbose tags are diagnostic contracts used by tests/log analysis.

## Test Signals
Signals include RTS recovery tests, dry-run stat tests, worker queue/thread-count tests, progress phase reporting, verbose tag assertions in log-based tests, active transaction/cursor preflight checks, and timestamp boundary rollback scenarios.
