# File Research: sources/os/linux/linux-stable/fs/ocfs2/suballoc.c

Implements OCFS2 suballocation for metadata blocks, dinodes, and global clusters. It manages chain allocator inodes, group descriptors, bitmap searches, allocation reservation contexts, block group growth, inode/metadata stealing across slots, free paths, and allocator locking for extent growth.

Key responsibilities:
- Validate and read group descriptors, including metadata ECC, signature, generation, parent dinode, chain index, free-count, bitmap size, and discontiguous group extent-list sanity.
- Reserve allocation contexts for metadata blocks, new inodes, local/global cluster allocation, and local allocator refill.
- Grow allocator inodes by creating new block groups, either contiguous or discontiguous when supported.
- Search allocation chains and group bitmaps for clear bits while respecting journal committed-data copies.
- Claim metadata blocks, dinodes, and clusters, updating allocator dinode counts and group bitmaps inside journal transactions.
- Free dinode/suballocator bits and cluster bits, with undo-buffer handling for global bitmap frees.
- Reclaim completely unused suballocator block groups back to the global bitmap.
- Provide helper APIs for inode-bit testing and allocator locking before extent-tree mutation.

Important behavior:
- `ocfs2_reserve_suballoc_bits()` locks a system allocator inode, ensures enough free bits, and optionally grows it by allocating a new block group.
- `ocfs2_block_group_alloc()` reserves global clusters for a new group, formats the descriptor, links it into the smallest chain, updates allocator inode size/counts, and caches the last allocation group.
- Discontiguous block groups store extents in `bg_list`; allocation results are adjusted back to physical block numbers through `ocfs2_bg_discontig_fix_result()`.
- `ocfs2_test_bg_bit_allocatable()` checks both the live bitmap and JBD2 committed copy to avoid reusing blocks freed by an uncommitted transaction.
- `ocfs2_claim_suballoc_bits()` tries the last-group hint, then the best free chain, then other chains, and can fall back to discontiguous main-bitmap allocation.
- `ocfs2_search_chain()` can relink a reasonably empty group toward the chain head to improve future allocation locality.
- `ocfs2_find_new_inode_loc()` supports a find-only reservation path; `ocfs2_claim_new_inode_at_loc()` later claims the exact location, used by ordering-sensitive inode creation flows.
- `__ocfs2_claim_clusters()` dispatches between local allocator and global bitmap allocation, clamps requests to bitmap group capacity, and returns cluster starts.
- `_ocfs2_free_suballoc_bits()` clears bitmap bits, updates chain/dinode counters, and may call `_ocfs2_reclaim_suballoc_to_main()` when a non-global suballocator group becomes empty.
- `ocfs2_lock_allocators()` reserves metadata and data allocators before extent growth so callers do not need to take allocator locks while holding an active journal handle.

Important exported APIs:
- Reservation: `ocfs2_reserve_new_metadata_blocks()`, `ocfs2_reserve_new_metadata()`, `ocfs2_reserve_new_inode()`, `ocfs2_reserve_clusters()`, `ocfs2_reserve_cluster_bitmap_bits()`.
- Claiming: `ocfs2_claim_metadata()`, `ocfs2_claim_new_inode()`, `ocfs2_find_new_inode_loc()`, `ocfs2_claim_new_inode_at_loc()`, `ocfs2_claim_clusters()`, `__ocfs2_claim_clusters()`.
- Freeing: `ocfs2_free_suballoc_bits()`, `ocfs2_free_dinode()`, `ocfs2_free_clusters()`, `ocfs2_release_clusters()`.
- Validation/utilities: `ocfs2_check_group_descriptor()`, `ocfs2_read_group_descriptor()`, `ocfs2_find_max_contig_free_bits()`, `ocfs2_which_cluster_group()`, `ocfs2_test_inode_bit()`, `ocfs2_lock_allocators()`.

Integration points:
- Heavily used by extent allocation/truncation, inode creation/deletion, local allocator, resize/recovery paths, quota-aware file growth, and system file lookup.
- Depends on OCFS2 journaling, metadata cache, local allocation, DLM inode locks, truncate-log freeing, and blockcheck validation.

Risk areas:
- Chain allocator counters, group free counts, and bitmaps must remain consistent across journal rollback/error paths.
- Reusing bits before delete/free transactions commit can corrupt data; committed bitmap-copy checks are central.
- Discontiguous group result translation is subtle because logical bitmap offsets may map to separate physical extents.
- Slot stealing improves availability but complicates allocator locality and lock ownership.
- Reclaiming empty suballocator groups rewrites both the suballocator and global bitmap in one transaction-sensitive path.
