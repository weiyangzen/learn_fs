# File Research: sources/os/linux/linux/fs/xfs/xfs_log_recover.c

## Purpose

`xfs_log_recover.c` implements XFS journal recovery. It locates the active portion of the circular on-disk log, validates record headers and CRCs, detects clean unmounts and torn writes, replays logged metadata items in ordered passes, processes recovered deferred intent work, rebuilds unlinked inode state, and finalizes recovery before normal filesystem operation resumes.

## Main Responsibilities

- Perform sector-aligned log I/O through `xlog_bread`, `xlog_bwrite`, and `xlog_do_io`.
- Find the log head and tail using cycle numbers, log record headers, and zeroed-log detection.
- Validate log record headers against log format, UUID, version, length, and CRC expectations.
- Detect and trim torn writes near the log head via CRC verification.
- Clear stale blocks beyond the discovered head so later crashes do not misidentify partial writes as valid records.
- Replay log transactions in two passes:
  - pass 1 gathers cancellation information, especially cancelled buffer items.
  - pass 2 replays buffers, inodes, dquots, quotaoff records, inode creation records, and intent/done item families.
- Reorder recovered transaction items to satisfy inode allocation, inode item, inode unlink buffer, and cancellation dependencies.
- Reconstruct transaction state from log operation headers, including split and continued regions.
- Process recovered intent items through deferred operation recovery.
- Recover AGI unlinked inode lists and leftover CoW staging extents after primary replay.
- Re-read and reinitialize the superblock after log replay.

## Key Data Flow

Recovery starts in `xlog_recover`. It calls `xlog_find_tail` to determine `head_blk` and `tail_blk`. If the log is dirty and recovery is allowed, it calls `xlog_do_recover`.

`xlog_do_recover` calls `xlog_do_log_recovery`, which allocates the buffer-cancel table and runs `xlog_do_recovery_pass` twice. After replay, it assigns the AIL tail, rereads the primary superblock buffer, refreshes in-core superblock features and counters, and clears active recovery state.

The second-stage public entrypoint is `xlog_recover_finish`. It runs recovered intents, forces the log, processes unlinked inode lists, and recovers leftover CoW staging extents. `xlog_recover_cancel` cancels pending recovered intents if mount recovery is abandoned.

## Important Functions

- `xlog_verify_bno`: bounds-checks log-relative block ranges.
- `xlog_alloc_buffer`: allocates log-sector-sized buffers, with extra space for unaligned sector handling.
- `xlog_header_check_recover`: rejects dirty logs with incompatible format or mismatched filesystem UUID.
- `xlog_header_check_mount`: validates mount-time log headers, tolerating old IRIX-style null UUID logs.
- `xlog_find_zeroed`: detects totally or partially zeroed logs and finds the first zero-cycle block.
- `xlog_find_head`: finds the next log write position, accounting for wraparound, incomplete writes, and partial records.
- `xlog_verify_head`: CRC-checks the possible in-flight log records near the head and trims torn writes.
- `xlog_verify_tail`: validates the tail and can advance it past overwritten tail records near the head.
- `xlog_clear_stale_blocks`: overwrites possible stale future-head blocks with empty records.
- `xlog_recover_reorder_trans`: sorts transaction items into replay-safe order.
- `xlog_recover_commit_trans`: commits a recovered transaction for a recovery pass.
- `xlog_recover_add_to_trans` and `xlog_recover_add_to_cont_trans`: assemble recovered log item regions, including split transaction headers and continued regions.
- `xlog_recover_process_ophdr`: validates operation headers, maps them to recovered transaction objects, and drains delayed-write buffers when recovery LSN changes.
- `xlog_recover_process`: CRC-checks, unpacks cycle data, and dispatches log record payload processing.
- `xlog_do_recovery_pass`: walks from tail to head, including physical-log wrap cases, and processes records.
- `xlog_recover_process_intents`: finishes recovered deferred intent work in log order.
- `xlog_recover_process_iunlinks`: scans AGI unlinked buckets and drives inodegc to finish deletion.
- `xlog_recover_iget` and `xlog_recover_iget_handle`: retrieve inodes for recovery, attach dquots, and validate inode generation when required.

## Recovery Ordering

The file explicitly documents and enforces replay order because metadata dependencies matter:

1. Non-cancelled buffers are replayed before most items.
2. Non-buffer items are replayed next.
3. Inode unlink buffers are replayed after inode items.
4. Cancelled buffers are processed last.

This avoids replaying stale cancelled buffers too early and ensures inode allocation/unlink dependencies are respected.

## Error Handling and Corruption Policy

The implementation treats unexpected log format, UUID mismatch, bad record lengths, invalid log block ranges, unknown operation clients, bad transaction headers, and unsupported log incompat bits as corruption or invalid recovery conditions. CRC mismatch is advisory for old non-CRC filesystems but fatal for CRC-enabled filesystems. I/O errors are surfaced unless the log is already shut down.

If recovery of intents fails, the code cancels pending intents, emits an alert, and shuts down the log. For CoW staging recovery failure, it forces shutdown but returns zero so already committed log items can be pushed through CIL/AIL.

## External Dependencies

This file depends heavily on XFS log internals, transaction item ops, buffer recovery, inode recovery, quota recovery, deferred ops, AIL, per-AG iteration, inodegc, and reflink recovery. It includes item ops for buffer, inode, dquot, quotaoff, icreate, EFI/EFD, RUI/RUD, CUI/CUD, BUI/BUD, ATTRI/ATTRD, XMI/XMD, and realtime intent families.

## Notable Edge Cases

- Totally zeroed logs are warned about because Linux XFS normally writes a dummy unmount record.
- Variable-length v2 log headers are supported, including compatibility handling for a known xfsprogs header-size bug.
- Log records and headers can wrap around the end of the physical circular log.
- Torn writes are tolerated only within the policy window of possible in-flight iclogs.
- Recovery can run on read-only mounts, but not on read-only underlying devices.
- Unknown v5 incompatible log features block recovery before any modification.
