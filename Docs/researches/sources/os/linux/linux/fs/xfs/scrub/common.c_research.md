# File Research: sources/os/linux/linux/fs/xfs/scrub/common.c

## Role
Provides shared infrastructure for XFS metadata scrubbers: error normalization, outcome flagging, AG and realtime group setup, transaction setup, inode acquisition, cross-reference gating, metadata inode checks, filesystem hook enablement, and inode block-count helpers.

## Error and Outcome Semantics
- `__xchk_process_error` and `__xchk_fblock_process_error` define the scrub convention: verifier and IO-style metadata errors become scrub flags and cleared error codes; operational errors remain return values; deadlock/retry conditions are traced for retry handling.
- Corruption, xref corruption, preen, warning, and incomplete states are set through small helper functions that also emit tracepoints.
- `xchk_should_check_xref` suppresses xref checks after primary corruption or after the relevant xref cursor fails, converting xref operational failures to `XFS_SCRUB_OFLAG_XFAIL`.

## AG and Realtime Group Setup
- `xchk_perag_read_headers`, `xchk_perag_drain_and_lock`, `xchk_ag_read_headers`, `xchk_ag_init`, and `xchk_ag_free` manage per-AG references, AGI/AGF buffers, intent draining, and btree cursors.
- `xchk_ag_btcur_init` creates bnobt/cntbt/rmapbt/refcountbt/inobt/finobt cursors as supported by the filesystem and drops cursors for metadata already known sick.
- Realtime helpers under `CONFIG_XFS_RT` acquire rtgroup references, lock rt metadata inodes, drain rt intents, and create realtime rmap/refcount cursors when needed.

## Transaction and Inode Setup
- `xchk_trans_alloc` chooses an empty transaction for scrub-only operations and a large repair reservation when repair is requested.
- `xchk_setup_fs`, `xchk_setup_rt`, and `xchk_setup_ag_btree` are common setup paths for filesystem, realtime, and AG btree scrubbers.
- `xchk_iget_for_scrubbing` safely resolves the target inode, including untrusted handle lookups, generation checks, AGI-protected fallback, and `ENOENT` handling for disappeared/free inodes.
- `xchk_setup_inode_contents` locks an inode for metadata-fork scrubbing with IOLOCK, transaction, optional dquot attachment, and ILOCK.

## Other Shared Helpers
- `xchk_count_rmap_ownedby_ag` counts rmap records owned by a given owner, respecting attr/data fork distinctions.
- `xchk_buffer_recheck` reruns buffer structural verifiers against in-memory buffers.
- `xchk_metadata_inode_forks` scrubs metadata inode records and forks, rejects realtime/reflink metadata inodes, and checks for shared blocks.
- `xchk_fsgates_enable` turns on runtime hooks for intent draining, quotas, directory entries, and rmap updates.
- `xchk_inode_is_allocated` examines incore inode cache state under AGI protection to decide whether an inode is allocated.
- `xchk_inode_is_dirtree_root`, `xchk_inode_is_sb_rooted`, and `xchk_inode_rootdir_inum` abstract root/metadir relationships.
- `xchk_inode_count_blocks` counts normal bmap fork blocks or metadata btree blocks for realtime metadata inodes.

## Invariants and Concurrency
- Scrub and repair hold AG header locks or rt metadata locks while checking cross-structure consistency and drain deferred intent chains if gates allow it.
- Inode references obtained during a transaction are released carefully to avoid VFS writeback paths needing another transaction.
- Cross-reference errors should not abort the primary scrub unless they are actual runtime errors; they mainly affect xref flags and cursor availability.
