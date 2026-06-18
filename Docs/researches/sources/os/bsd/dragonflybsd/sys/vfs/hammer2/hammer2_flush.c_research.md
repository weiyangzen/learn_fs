# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_flush.c

## Purpose
Implements HAMMER2 transaction accounting and recursive COW flush propagation. It converts modified chain state into updated media blockrefs, manages parent block-table updates, flushes freemap and topology roots, and coordinates volume-header synchronization.

## Transaction Handling
- `hammer2_trans_init()` increments per-PFS transaction state and serializes flush transactions against other flushes. Buffer-cache transactions are allowed through to avoid deadlocks.
- `hammer2_trans_sub()` allocates a new cluster-level modify tid (`modify_tid`) for sequenced XOPs inside a transaction.
- `hammer2_trans_setflags()` and `hammer2_trans_clearflags()` modify transaction state atomically and wake waiters when `HAMMER2_TRANS_WAITING` clears.
- `hammer2_trans_done()` decrements the transaction count, clears flags supplied by the caller, and wakes waiters when a flush completes or pending flushes can proceed.
- `hammer2_trans_newinum()` atomically allocates inode numbers.
- `hammer2_trans_assert_strategy()` is currently permissive; historical assertions disallowing strategy during flush are disabled.

## Flush Algorithm
- `hammer2_flush()` prepares a `hammer2_flush_info` context, references the parent and target chain, and repeatedly invokes `hammer2_flush_core()` until parent movement no longer requires retry.
- `hammer2_flush_core()` is the main recursive state machine:
  - Returns quickly if no flush-relevant chain flags are present.
  - Stops at mounted PFS boundaries unless `HAMMER2_FLUSH_ALL` is requested, while preserving parent `ONFLUSH` if work remains below.
  - Optionally stops at inode boundaries for `HAMMER2_FLUSH_INODE_STOP`.
  - Recurses down on `ONFLUSH` or `DESTROY`, then performs bottom-up work.
  - Locks parent then child in the required order before modifying parent block tables.
  - Clears `MODIFIED`, updates checksums/statistics, handles destroyed chains, and processes `UPDATE`.
- `hammer2_flush_recurse()` is the RB-tree child scanner. It references children before dropping the parent spinlock, handles parent movement races, propagates destroy state, and skips hidden PFS-root inode-index entries during non-filesystem-sync flushes.

## Media-Specific Flush Behavior
- `HAMMER2_BREF_TYPE_FREEMAP`: updates `voldata.freemap_tid`, asserts vchain is modified, and bumps `voldata.mirror_tid` so topology and freemap recovery remain distinguishable.
- `HAMMER2_BREF_TYPE_VOLUME`: locks fchain, updates `voldata.mirror_tid`, computes sector and full-header iCRCs, copies `voldata` to `volsync`, and marks `HAMMER2_CHAIN_VOLUMESYNC`.
- `DATA`: assumes data has already been written through file buffer-cache paths.
- `INDIRECT`, `FREEMAP_NODE`, `FREEMAP_LEAF`, non-inline `DIRENT`, and `INODE`: recompute chain checks; PFS-root inodes also copy `pmp->inode_tid` into media.
- Destroyed modified chains have dedup candidacy deleted and have disabled code for DIO invalidation.

## Parent Block-Table Updates
- `UPDATE` with no parent is simply cleared.
- Non-FSSYNC inode flushes with `HAMMER2_FLUSH_INODE_STOP` intentionally avoid updating the parent block table, preserving dependency ordering across crashes.
- Destroyed parents skip real block-table rewrites and only carry forward the child's modify tid.
- Indirect blocks receive maintenance for deletion/collapse before parent updates.
- Parent modification errors, including ENOSPC, are accumulated but do not abort recursive flushing; the child `UPDATE` flag is restored.
- Parent blockref arrays are selected from inode embedded blocksets, indirect/freemap-node arrays, volume super-root blockset, or freemap array depending on parent type.

## Backend Flush XOP
- `hammer2_xop_inode_flush()` flushes a single inode chain for a cluster element, optionally with inode-stop, filesystem-sync, and volume-header flags.
- For PFS roots, it can flush the super-root, fchain, vchain, device buffers, and then a rotated volume header.
- Device buffers are fsynced before writing `volsync` to the selected volume-header slot.
- The volume header write is preceded by a device `BUF_CMD_FLUSH` for ordering.

## Concurrency and Failure Notes
- Uses atomic chain flags, chain refs/holds, chain locks, spinlocks for child RB scans, and transaction wait channels.
- Parent-child races are explicitly detected as `LOST CHILD` cases and retried or skipped.
- Recursion depth above 60 panics rather than deferring; the surrounding comments describe deferral support, but current code uses a hard panic.
- Flush errors are cumulative in `info.error`, but later buffer writeback errors may occur after the flush call returns.
