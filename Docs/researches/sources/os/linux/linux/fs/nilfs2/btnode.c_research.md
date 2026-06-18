# File Research: sources/os/linux/linux/fs/nilfs2/btnode.c

This file implements the dedicated page-cache layer used for NILFS2 B-tree node blocks. It initializes “btnc” associated inodes, clears their caches, creates new node buffers, submits node reads, deletes cached node buffers, and supports changing a node block’s cache key when a logical/virtual node address changes.

Key behaviors:
- `nilfs_init_btnc_inode()` turns an associated inode into a regular buffer-cache-only inode using `nilfs_buffer_cache_aops` and `GFP_NOFS`.
- `nilfs_btnode_create_block()` grabs a cache buffer by B-tree node block number, rejects already mapped/uptodate/dirty buffers as duplicate block-address use, zeroes the block, and marks it mapped/uptodate.
- `nilfs_btnode_submit_block()` reads a node block, optionally translating virtual block numbers through DAT except for the DAT inode itself. It uses internal `-EEXIST` for cache hits and `-EBUSY` for failed readahead locking/contiguity.
- `nilfs_btnode_delete()` forgets a buffer, waits for writeback, and invalidates the containing folio if no dirty buffers remain.
- The change-key trio prepares, commits, or aborts relocation of a cached node from `oldkey` to `newkey`. If block size equals page size, it tries an xarray folio move; otherwise it creates a new buffer and copies data.

Important invariants:
- Existing mapped/dirty/uptodate buffers at a supposedly new node key are treated as metadata inconsistency.
- Full-folio key changes hold the folio lock between prepare and commit/abort while the same folio is temporarily present at the new xarray index.
- The current implementation explicitly does not support folio sizes larger than page size.
- Callers must handle internal return codes from read submission and must release returned buffer heads.

Dependencies:
- Uses `nilfs_grab_buffer()`, `nilfs_forget_buffer()`, `nilfs_copy_buffer()`, and `nilfs_buffer_cache_aops` from NILFS page/buffer helpers.
- Uses DAT translation through `nilfs_dat_translate()` for virtual B-tree node block numbers.
