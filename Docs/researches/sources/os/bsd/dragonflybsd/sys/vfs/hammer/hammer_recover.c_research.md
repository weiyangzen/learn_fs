# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_recover.c

Purpose: implements mount-time recovery. Stage 1 replays raw UNDO records backward to restore metadata consistency. Stage 2 replays logical REDO records forward when REDO recovery is required.

Stage 1: `hammer_recover_stage1()` reads the root volume UNDO blockmap, validates FIFO indices, and for version 4+ filesystems discovers the real active FIFO range by scanning backward for the prior sequence number then forward until sequence discontinuity. It scans the active range backward, applies each UNDO via `hammer_recover_undo()`, and records the first backward-seen `HAMMER_REDO_SYNC` as the stage2 extended-range start. It updates root volume FIFO indices to the recovered range and flushes or discards recovered buffers depending on success and read-only mode.

UNDO execution: `hammer_recover_undo()` accepts only UNDO records, validates payload size and target offset, and restores bytes into either raw volume headers or raw metadata buffers without generating new UNDO. Recovered buffers/volumes are marked so the recovery flush routine can delay or discard writes safely.

Stage 2: `hammer_recover_stage2()` runs only on read-write mounts or read-only-to-read-write transition. It respects tunable `vfs.hammer.skip_redo`. It computes the nominal UNDO range and REDO extended range from `recover_stage2_offset`, backward-scans the extended-only area to collect `REDO_TERM_WRITE`/`REDO_TERM_TRUNC` records into an RB tree, then forward-scans the full extended range and executes `REDO_WRITE` or `REDO_TRUNC` records that do not have matching termination records.

REDO execution: `hammer_recover_redo_exec()` starts a transaction, finds the inode by object id/localization, obtains its vnode, and performs either `vn_rdwr()` for write payloads or `VOP_SETATTR()` for truncation. REDO recovery disables recursive REDO semantics through mount flags handled by the REDO generator.

FIFO scanning and validation: `hammer_recover_scan_rev()` and `hammer_recover_scan_fwd()` walk circular UNDO space while handling wraparound. Signature helpers verify head/tail signatures, alignment, record size, buffer-boundary containment, type/size agreement, and CRC for non-PAD records.

Flush handling: `hammer_recover_flush_buffers()` writes recovered buffers first, then volume headers, with the root volume header flushed last on final success. With `final < 0`, it clears error/modified state and discards recovered buffers for failed or read-only recovery teardown.

Risk surface: this file is the crash-consistency center for HAMMER. Sequence monotonicity, FIFO wrap detection, and the distinction between nominal UNDO range and extended REDO range are critical to avoiding replaying stale logical operations.
