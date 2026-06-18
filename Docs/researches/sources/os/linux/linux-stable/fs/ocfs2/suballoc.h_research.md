# File Research: sources/os/linux/linux-stable/fs/ocfs2/suballoc.h

Declares the OCFS2 suballocator API implemented by `suballoc.c`.

Key contents:
- Defines `group_search_t`, the callback signature for searching one group descriptor bitmap.
- Defines `struct ocfs2_alloc_context`, the reservation/claim state object used for metadata, inode, local allocator, main bitmap, and discontiguous main bitmap allocations.
- Defines allocation context modes: `OCFS2_AC_USE_LOCAL`, `OCFS2_AC_USE_MAIN`, `OCFS2_AC_USE_INODE`, `OCFS2_AC_USE_META`, and `OCFS2_AC_USE_MAIN_DISCONTIG`.
- Tracks allocator inode and buffer, target slot, requested/given bits, current chain, search callback, last group hint, max block limit, find-location-only state, and optional reservation map.

Declared APIs:
- Context lifetime: `ocfs2_free_alloc_context()`, `ocfs2_free_ac_resource()`, `ocfs2_alloc_context_bits_left()`.
- Reservation: `ocfs2_reserve_new_metadata()`, `ocfs2_reserve_new_metadata_blocks()`, `ocfs2_reserve_new_inode()`, `ocfs2_reserve_clusters()`, `ocfs2_reserve_cluster_bitmap_bits()`.
- Claiming: `ocfs2_claim_metadata()`, `ocfs2_claim_new_inode()`, `ocfs2_claim_new_inode_at_loc()`, `ocfs2_find_new_inode_loc()`, `ocfs2_claim_clusters()`, `__ocfs2_claim_clusters()`.
- Bitmap mutation/freeing: `ocfs2_block_group_set_bits()`, `ocfs2_free_suballoc_bits()`, `ocfs2_free_dinode()`, `ocfs2_free_clusters()`, `ocfs2_release_clusters()`.
- Validation/helpers: `ocfs2_check_group_descriptor()`, `ocfs2_read_group_descriptor()`, `ocfs2_find_max_contig_free_bits()`, `ocfs2_which_cluster_group()`, `ocfs2_is_cluster_bitmap()`, `ocfs2_lock_allocators()`, `ocfs2_test_inode_bit()`, `ocfs2_init_steal_slots()`.

Important inline behavior:
- `ocfs2_which_suballoc_group()` derives a contiguous group descriptor block from an allocated block and bit.
- `ocfs2_cluster_from_desc()` maps cluster bitmap group descriptor blocks to cluster offsets, with special handling for the first group.
- `ocfs2_is_cluster_bitmap()` identifies the global bitmap inode by comparing inode block number to `osb->bitmap_blkno`.

Risk areas:
- Callers own high-level locking and must pair reservation contexts with frees.
- `ac_find_loc_only` and `ac_find_loc_priv` are specialized ordering hooks; misuse can claim a different block than the caller expects.
- `ocfs2_which_suballoc_group()` is not sufficient for discontiguous groups when an explicit `i_suballoc_loc` exists.
