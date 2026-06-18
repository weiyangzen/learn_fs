# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_log.c

## Purpose

`xfs_log.c` implements the core XFS journal/log manager: log mount and recovery setup, log space reservation, in-core log buffer state transitions, physical log writes, log force operations, unmount records, log covering, ticket lifecycle, forced shutdown, and metadata LSN validation.

It is the central coordinator between transaction reservation accounting, the CIL layer in `xfs_log_cil.c`, iclog buffers, the AIL, recovery, block I/O, and mount shutdown state.

## Major Responsibilities

- Allocate and initialize `struct xlog` and its ring of `struct xlog_in_core` buffers.
- Reserve and regrant log space through reserve and write grant heads.
- Serialize log writers into active iclogs and flush iclogs to the on-disk log.
- Handle log wrapping, cycle stamping, v2 log extended headers, checksums, FUA/prefetch flush ordering, and split writes at physical log end.
- Force all or selected checkpoint sequences to stable storage.
- Write unmount records and cover idle logs with dummy/superblock transactions.
- Process iclog completion callbacks in LSN order.
- Shut down the log safely and wake all waiters.
- Validate metadata LSNs against the current log head.

## Key Data and Control Flow

The log uses two grant heads, `l_reserve_head` and `l_write_head`, to track reserved and writable space. `xfs_log_reserve` allocates a ticket, checks available grant space, and advances both grant heads. `xfs_log_regrant`, `xfs_log_ticket_regrant`, and `xfs_log_ticket_ungrant` adjust grant accounting for rolling and completed transactions.

`xlog_state_get_iclog_space` gives writers space in the current active iclog. If the current iclog is full or nearly full, it switches the iclog to `XLOG_STATE_WANT_SYNC` and advances the ring. `xlog_write` copies log vectors into iclogs, using `xlog_write_full` for vectors that fit and `xlog_write_partial` for regions that must continue across iclogs.

`xlog_sync` prepares an iclog for disk: computes rounded size, stamps cycle numbers into each basic block, fills record length and checksum, handles split writes across the physical log end, and submits the bio through `xlog_write_iclog`. Completion is deferred to `xlog_ioend_work`, which detects I/O errors and advances the iclog completion state machine.

The iclog state machine flows through active, want-sync, syncing, done-sync, callback, dirty, and back to active. `xlog_state_done_syncing`, `xlog_state_do_callback`, and `xlog_state_clean_iclog` preserve ordered callback execution so CIL checkpoint completion and AIL insertion happen in log order.

## Mount, Recovery, and Unmount

`xfs_log_mount` allocates the log, validates minimum log size, initializes the AIL, runs recovery unless mounted norecovery, creates sysfs state, clears active recovery, and initializes the CIL post-recovery ticket. `xfs_log_mount_finish` completes phase-two recovery after mount inodes are available, forces recovered work to disk, drains buffers, and clears recovery-needed state.

Unmount and quiesce paths use `xfs_log_quiesce`, `xfs_log_clean`, and `xfs_log_unmount_write`. Clean unmount writes an unmount record unless the filesystem is not writable, shutdown, or summary counters are marked sick and should be recalculated on next mount.

## Log Covering

The file implements the XFS cover state machine (`XLOG_STATE_COVER_*`) that writes dummy/superblock transactions when the log is idle. This advances the on-disk tail so old allocation transactions do not replay unnecessarily after a crash. Covering requires CIL empty, AIL empty, and iclogs empty.

## Concurrency and Ordering

Important locks and barriers:

- `l_icloglock` protects iclog ring state, current head position, and iclog state transitions.
- Grant head locks protect waiter lists but fast paths avoid taking them where possible.
- `smp_rmb`/`smp_wmb` pair grant space calculations with AIL tail-space updates.
- I/O completion work uses per-iclog semaphores to serialize unmount teardown against pending I/O.
- Force paths set `XLOG_ICL_NEED_FLUSH` and `XLOG_ICL_NEED_FUA` to preserve metadata/log ordering on stable storage.

## Error Handling

`xlog_force_shutdown` is the global shutdown path. It optionally forces the log first, atomically marks `XLOG_IO_ERROR`, sets mount shutdown state, wakes reservation and force waiters, wakes CIL waiters, runs pending callbacks, and wakes zoned RT waiters where applicable. Shutdown paths are careful not to recurse into log writes after log I/O errors.

## External Interfaces

Important exported or cross-file functions include:

- `xfs_log_mount`, `xfs_log_mount_finish`, `xfs_log_mount_cancel`
- `xfs_log_reserve`, `xfs_log_regrant`
- `xlog_write`, `xlog_write_one_vec`
- `xfs_log_force`, `xfs_log_force_seq`
- `xfs_log_quiesce`, `xfs_log_clean`, `xfs_log_unmount`
- `xlog_assign_tail_lsn`, via related header declarations
- `xlog_force_shutdown`
- `xfs_log_check_lsn`

## Research Notes

This file is performance-sensitive and correctness-sensitive. The most important invariants are grant accounting must not overrun log tail space, iclog callbacks must run in LSN order, commit records that imply stable ordering must set flush/FUA requirements, and log wrap must update block before cycle so unlocked LSN validation does not see a transient future LSN.
