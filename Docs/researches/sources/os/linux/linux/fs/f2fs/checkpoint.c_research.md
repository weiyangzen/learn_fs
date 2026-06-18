# File Research: sources/os/linux/linux/fs/f2fs/checkpoint.c

## Purpose
Implements F2FS checkpoint coordination, metadata page IO, checkpoint pack validation/writing, orphan inode tracking/recovery, dirty inode synchronization, checkpoint request merging, and checkpoint-thread lifecycle.

## Main Responsibilities
- Wraps F2FS rwsem operations with optional priority uplift and lock latency tracing.
- Reads, writes, dirties, validates, and readaheads metadata folios.
- Validates block addresses against metadata/data regions and SIT bitmaps.
- Tracks inode sets for orphan, append, update, transition-directory, and flush state using radix trees and lists.
- Recovers orphan inodes at mount and writes orphan lists during checkpoints.
- Selects valid checkpoint packs by CRC and version.
- Freezes filesystem operations for checkpoint, flushes dirty dentry/node/inode metadata, writes NAT/SIT/summary/checkpoint data, and commits the final checkpoint page with flush semantics.
- Supports asynchronous merged checkpoint requests through a kernel thread.

## Key Functions and Flows
- Metadata IO: `f2fs_grab_meta_folio()`, `f2fs_get_meta_folio()`, `f2fs_ra_meta_pages()`, `f2fs_sync_meta_pages()`, and `f2fs_meta_aops`.
- Address validation: `f2fs_is_valid_blkaddr()` and raw variant enforce legal ranges for NAT/SIT/SSA/CP/POR/data/meta access.
- Orphans: `f2fs_acquire_orphan_inode()`, `f2fs_add_orphan_inode()`, `f2fs_recover_orphan_inodes()`, and `write_orphan_inodes()`.
- Checkpoint loading: `validate_checkpoint()` checks first/last CP block versions and CRC, while `f2fs_get_valid_checkpoint()` chooses the newest valid pack.
- Dirty inode sync: `f2fs_update_dirty_folio()`, `f2fs_sync_dirty_inodes()`, and `f2fs_sync_inode_meta()`.
- Checkpoint write: `f2fs_write_checkpoint()` locks global checkpoint state, blocks filesystem operations, flushes NAT/SIT, then calls `do_checkpoint()`.
- Commit: `do_checkpoint()` updates checkpoint fields, writes bitmaps, checkpoint payload, orphan blocks, summaries, flushes metadata, flushes devices, commits the final CP page, and flips current CP pack.
- Async checkpoints: `f2fs_issue_checkpoint()`, `issue_checkpoint_thread()`, and related request-control helpers merge synchronous checkpoint requests when configured.

## Concurrency and Recovery Notes
- `cp_rwsem`, `cp_global_sem`, `node_change`, `node_write`, and `gc_lock` enforce checkpoint ordering.
- `block_operations()` loops until quotas, dirty dentries, inode metadata, and dirty node pages are quiesced.
- Checkpoint errors cause early `-EIO`, stop checkpointing, and may mark `SBI_NEED_FSCK`.
- `commit_checkpoint()` writes the last checkpoint block with `META_FLUSH`, making it the atomic commit point for the pack.
