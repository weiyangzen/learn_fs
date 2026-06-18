# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_thread.c

## Purpose

`lufs_thread.c` implements the per-log roll thread that copies committed logmap deltas back to their master filesystem locations and frees log space. It is the asynchronous cleaner that keeps the physical log from filling.

## Main Interfaces

Important routines are `trans_roll`, `log_roll_read`, `log_roll_write`, `log_roll_write_crb`, `log_roll_write_bufs`, and the static helpers `trans_roll_wait` and `log_roll_buffers`.

Tunables include roll buffer count limits, `logmap_maxnme`, `trans_roll_tics`, and counters for new-delta/read-wait behavior.

## Behavior And Data Flow

`trans_roll()` allocates a configurable number of `MAPBLOCKSIZE` roll buffers, marks its thread-specific state to bypass snapshot throttling, then loops until exit/error. It rolls when forced, when the logmap is too full, when the log is idle but nonempty, or when physical log usage is high.

`log_roll_read()` finds a committed map block to roll, obtains logmap entries under the logmap reader lock, uses cached roll buffers when available, otherwise reads the master block and overlays deltas from the log. It avoids spinning if entries are in use by taking the logmap writer lock and retrying later.

`log_roll_write()` sorts roll buffers by block number, issues writes, waits for all master writes and cloned subwrites, and reports errors through `ldl_seterror()`.

## Snapshot And I/O Handling

Roll writes go through `fssnap_strategy()` when snapshots are active, otherwise through `bdev_strategy()`. Cached roll buffers can be written directly. Non-cached roll buffers use a sector map so only metadata sectors are written when a full master-block write could overwrite user data.

## Notable Invariants And Risks

- The roll thread exits through `MTM_ROLL_EXIT` or `LDL_ERROR` and broadcasts waiters.
- `MT_SCAN` debug mode suppresses normal rolling unless forced.
- Force-roll waiters are released after a complete force-roll cycle.
- Audit hotspots are ordering of sorted writes, cloned buffer cleanup, handling of `B_INVAL` roll buffers, snapshot bypass deadlock avoidance, and wakeup/exit flag transitions.
