# File Research: sources/os/linux/linux/fs/xfs/xfs_log.c

## Purpose

`xfs_log.c` is the central XFS log manager implementation. It owns log allocation and teardown, log-space reservation grant heads, in-core log buffer (`iclog`) state transitions, physical log writes, log forcing, clean unmount record writing, log covering, shutdown propagation, and LSN validation.

This file bridges transaction/CIL code and the block layer: callers reserve or regrant tickets, `xlog_write()` copies formatted log vectors into iclogs, iclog state transitions eventually submit bios to the log device, and completion callbacks move committed CIL contexts into the AIL.

## Major Responsibilities

- Mount-time log setup in `xfs_log_mount()`: allocate `struct xlog`, validate minimum log size, initialize AIL, perform recovery unless `norecovery`, create sysfs state, clear active recovery, and initialize CIL post-recovery.
- Recovery finish/cancel paths in `xfs_log_mount_finish()` and `xfs_log_mount_cancel()`.
- Unmount/quiesce paths: `xfs_log_quiesce()`, `xfs_log_clean()`, `xfs_log_unmount()`, and unmount-record writing through `xfs_log_unmount_write()` / `xlog_unmount_write()`.
- Reservation grant accounting: `xfs_log_reserve()`, `xfs_log_regrant()`, `xfs_log_ticket_regrant()`, `xfs_log_ticket_ungrant()`, and helpers around reserve/write grant heads.
- In-core log buffer ring management: allocation, state changes, space acquisition, sync submission, completion, activation, callback running, and shutdown cleanup.
- Log writing: `xlog_write()`, `xlog_write_one_vec()`, full/partial log-vector copying, continuation opheaders, record counts, ticket accounting, and split-region handling across iclogs.
- Physical IO: cycle stamping, log checksum calculation, optional split writes across physical log wrap, block-layer bio submission, preflush/FUA handling, external-log data-device flush ordering, and async IO-end workqueue callback.
- Log force APIs: `xfs_log_force()` and `xfs_log_force_seq()` force current iclogs or CIL checkpoint sequences to stable storage.
- Forced shutdown: `xlog_force_shutdown()` serializes shutdown, optionally forces the log first, marks log/mount shutdown, wakes grant/CIL/iclog waiters, processes callbacks, and wakes zoned RT waiters.
- LSN validity: `xfs_log_check_lsn()` warns when metadata LSNs are ahead of the current log head.

## Key Data Flow

1. Transaction code obtains a `struct xlog_ticket` via `xfs_log_reserve()`.
2. CIL or direct log code passes a chain of `struct xfs_log_vec` to `xlog_write()`.
3. `xlog_state_get_iclog_space()` chooses the current active iclog, stamps a header LSN on first use, reserves space, and may switch full iclogs to `WANT_SYNC`.
4. `xlog_write_full()` or `xlog_write_partial()` copies log iovecs into the iclog data area, adding continuation opheaders when a region spans iclogs.
5. `xlog_state_release_iclog()` drops the writer reference. If this was the last reference and the iclog wants sync, it transitions to `SYNCING` and calls `xlog_sync()`.
6. `xlog_sync()` rounds the record size, cycle-stamps 512-byte blocks, records the tail LSN, computes CRC, and submits the write with `xlog_write_iclog()`.
7. IO completion queues `xlog_ioend_work()`, which calls `xlog_state_done_syncing()`.
8. Completion state processing runs CIL callbacks via `xlog_cil_process_committed()`, cleans dirty iclogs back to active order, wakes waiters, and advances covering state.

## Important Functions and Mechanics

- `xlog_grant_space_left()` calculates available grant space as log size minus tail-pinned bytes minus grant-head usage. It has an explicit read barrier paired with CIL AIL insertion so grant head and tail updates are observed in the right order.
- `xlog_grant_head_check()` implements the fast path for log-space reservations without taking the grant-head lock unless waiters exist or free space is insufficient.
- `xlog_grant_head_wait()` sleeps uninterruptibly, pushes the AIL to free log space, and exits with `-EIO` on shutdown.
- `xfs_log_writable()` rejects writes for norecovery mounts, read-only data/log devices, or shutdown logs, while allowing readonly mounts to perform internal recovery/unmount operations.
- `xlog_force_iclog()` marks an iclog for preflush and FUA, switches active iclogs when needed, and releases it for syncing.
- `xlog_wait_on_iclog()` waits on `ic_force_wait` unless the iclog is already active/dirty or the log is shut down.
- `xlog_state_switch_iclogs()` marks the current iclog `WANT_SYNC`, stamps previous-block linkage, advances the log head block/cycle with wrap handling, and moves the ring head to the next iclog.
- `xlog_force_and_check_iclog()` handles synchronous or very fast async devices by detecting if the iclog completed and was reused before the force caller starts waiting.
- `xlog_calc_unit_res()` computes transaction reservation overhead for opheaders, transaction headers, iclog headers, split records, commit record headers, and roundoff padding.
- `xlog_ticket_alloc()` allocates ticket state from `xfs_log_ticket_cache`, initializes reservation counts, random transaction id, and permanent-reservation flag.
- Debug-only `xlog_verify_tail_lsn()` and `xlog_verify_iclog()` check log-space safety, iclog ring integrity, magic numbers, client ids, and operation lengths before IO.

## State Machines and Invariants

- Iclog states flow through `ACTIVE -> WANT_SYNC -> SYNCING -> DONE_SYNC -> CALLBACK -> DIRTY -> ACTIVE`, with `DIRTY` iclogs reactivated only in ring order to preserve log ordering.
- `ic_refcnt` prevents an iclog from being synced while writers are still copying data. Last release of a `WANT_SYNC` iclog submits IO.
- `XLOG_ICL_NEED_FLUSH` and `XLOG_ICL_NEED_FUA` enforce stable-storage ordering for forced log records and CIL checkpoint commits.
- Log covering uses `XLOG_STATE_COVER_IDLE/NEED/DONE/NEED2/DONE2`. Two dummy superblock transactions are used to move the on-disk tail past potentially replayable allocation transactions when the filesystem becomes idle.
- `xlog_state_release_iclog()` records the current log tail into the iclog header when the iclog first needs FUA or wants sync, and avoids later changes to preserve checkpoint ordering.
- Log head updates on wrap write `l_curr_block` before incrementing `l_curr_cycle`; this ordering supports lockless validation in `xlog_valid_lsn()`.
- Shutdown state is protected by `XLOG_SHUTDOWN_STARTED` and `XLOG_IO_ERROR`, and much of the iclog state machine assumes shutdown cannot change while `l_icloglock` is held.

## Error and Shutdown Behavior

- IO errors, injected IO errors, failed external-log data-device flushes, or injected CRC failures force shutdown with `SHUTDOWN_LOG_IO_ERROR`.
- Reservation failures after shutdown return `-EIO`; tickets are zeroed so cancel/ungrant paths do not return bogus reservation space.
- `xlog_state_shutdown_callbacks()` processes callbacks only for unreferenced iclogs, wakes force/write/flush waiters, and is re-run by last iclog release if a referenced iclog delayed callback processing.
- `xlog_force_shutdown()` avoids log force for recovery or log IO error shutdowns, wakes grant queues and CIL wait queues, runs pending callbacks, and marks the mount shutdown if needed.
- `xfs_log_mount_finish()` asserts that a failed recovery finish leaves the log shut down.

## Dependencies and Coupling

- Uses CIL interfaces from `xfs_log_cil.c` for checkpoint flushing, commit callback processing, and empty checks.
- Uses AIL functions to push pinned metadata, insert committed items indirectly via callbacks, and update log tail/free space.
- Uses block-layer `bio`, `REQ_PREFLUSH`, `REQ_FUA`, `REQ_META`, and optional bio splitting for physical log wrap.
- Uses mount/superblock helpers for log geometry, lazysb counters, log incompat feature clearing, read-only checks, health flags, and sysfs registration.
- Uses tracepoints and XFS stats extensively around grant, force, iclog, and unmount paths.

## Notable Edge Cases

- External log devices require flushing the data device before log IO if the iclog has `NEED_FLUSH`, because metadata writeback covered by the LSN must be stable before the external log record.
- Log writes that straddle the physical end of the log are split into two bios and have cycle numbers adjusted for the wrapped portion.
- Partial region writes must never create an empty first continuation segment, because recovery would skip it and mis-associate continuation data.
- `xfs_log_unmount_write()` deliberately skips clean unmount records if summary counters are sick or an error tag requests summary recalculation, forcing next-mount recovery.
- `xfs_log_check_lsn()` treats norecovery and NULL LSNs as valid, but warns when metadata appears ahead of the current log head.

## Research Notes

This file is the durability-critical path for XFS metadata journaling. Correctness depends on three ordering layers working together: grant-head accounting vs. AIL tail updates, CIL checkpoint ordering vs. iclog callback order, and block-device cache ordering via preflush/FUA. The implementation prefers global ordering through the iclog ring rather than out-of-order reuse of free iclogs, simplifying recovery assumptions at the cost of potential sleeps when all iclogs are in flight.
