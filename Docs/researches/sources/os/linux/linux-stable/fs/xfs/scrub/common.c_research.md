# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/common.c

## Role

Shared infrastructure for XFS scrubbers. It centralizes scrub error handling, corruption/preen/warning flag reporting, transaction setup, AG and realtime group resource acquisition, inode lookup, inode locking, cross-reference gating, and metadata inode helpers.

## Key Functions

- `xchk_process_error()`, `xchk_fblock_process_error()`, and xref variants convert operational errors into scrub flags and trace events.
- `xchk_*_set_{corrupt,preen,warning}()` record scrub outcomes at filesystem, block, inode, quota, and file-offset granularity.
- `xchk_ag_init()`, `xchk_perag_drain_and_lock()`, and `xchk_ag_btcur_init()` lock AG headers, wait for intent chains, and create cross-reference cursors.
- `xchk_rtgroup_init()`, `xchk_rtgroup_lock()`, and cleanup helpers do the same for realtime group metadata under `CONFIG_XFS_RT`.
- `xchk_trans_alloc()` chooses empty transactions for scrub and repair-sized transactions for repair.
- `xchk_iget_for_scrubbing()`, `xchk_iget_agi()`, and `xchk_iget_safe()` safely acquire potentially untrusted inodes while avoiding inode btree deadlocks.
- `xchk_setup_inode_contents()` locks inode contents, allocates transactions, attaches dquots for repair, and prepares inode fork scrubbers.
- `xchk_should_check_xref()` disables broken xref cursors without aborting the primary scrub.
- `xchk_metadata_inode_forks()` scrubs metadata inode records and forks and rejects realtime/reflink misuse.
- `xchk_fsgates_enable()` enables runtime hooks for intent draining, quotas, dirents, and rmap updates.
- `xchk_inode_is_allocated()` checks incore inode allocation state while the AGI is locked.
- `xchk_inode_count_blocks()` handles normal and metadata-btree-backed inode block counting.

## Research Notes

This file defines the scrubber contract: verifier corruption is reported through flags, transient/runtime failures propagate as errno, and cross-reference failures are isolated from primary metadata checks. It is also the central lock-order and resource-lifetime coordinator for scrub and repair.
