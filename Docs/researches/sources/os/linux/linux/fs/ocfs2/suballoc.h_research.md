# File Research: sources/os/linux/linux/fs/ocfs2/suballoc.h

## Purpose

`suballoc.h` declares the OCFS2 suballocator API and defines `struct ocfs2_alloc_context`, the shared reservation/claim state used by inode, metadata, and cluster allocation paths.

## Key Types and Fields

`group_search_t` is the callback type used by allocation contexts to search a group descriptor for suitable bits.

`struct ocfs2_alloc_context` contains:

- `ac_inode`: allocator bitmap inode.
- `ac_bh`: allocator dinode buffer.
- `ac_alloc_slot`: slot associated with allocator.
- `ac_bits_wanted` / `ac_bits_given`: reservation accounting.
- `ac_which`: allocator source:
  - `OCFS2_AC_USE_LOCAL`
  - `OCFS2_AC_USE_MAIN`
  - `OCFS2_AC_USE_INODE`
  - `OCFS2_AC_USE_META`
  - `OCFS2_AC_USE_MAIN_DISCONTIG`
- Chain-search state: `ac_chain`, `ac_disable_chain_relink`, `ac_group_search`, `ac_last_group`, and `ac_max_block`.
- Find-location-only state for ordering-sensitive inode creation: `ac_find_loc_only`, `ac_find_loc_priv`.
- `ac_resv`: reservation record for local allocation reservations.

## API Surface

Reservation:

- `ocfs2_init_steal_slots()`
- `ocfs2_reserve_new_metadata()`
- `ocfs2_reserve_new_metadata_blocks()`
- `ocfs2_reserve_new_inode()`
- `ocfs2_reserve_clusters()`
- `ocfs2_reserve_cluster_bitmap_bits()`

Claim:

- `ocfs2_claim_metadata()`
- `ocfs2_claim_new_inode()`
- `ocfs2_find_new_inode_loc()`
- `ocfs2_claim_new_inode_at_loc()`
- `ocfs2_claim_clusters()`
- `__ocfs2_claim_clusters()`

Free/release:

- `ocfs2_free_alloc_context()`
- `ocfs2_free_ac_resource()`
- `ocfs2_free_suballoc_bits()`
- `ocfs2_free_dinode()`
- `ocfs2_free_clusters()`
- `ocfs2_release_clusters()`

Helpers:

- `ocfs2_alloc_context_bits_left()`
- `ocfs2_which_suballoc_group()`
- `ocfs2_cluster_from_desc()`
- `ocfs2_is_cluster_bitmap()`
- `ocfs2_which_cluster_group()`
- `ocfs2_find_max_contig_free_bits()`
- `ocfs2_block_group_set_bits()`
- `ocfs2_read_group_descriptor()`
- `ocfs2_check_group_descriptor()`
- `ocfs2_lock_allocators()`
- `ocfs2_test_inode_bit()`

## Correctness Notes

- The header explicitly requires callers to pass the root extent list to `ocfs2_reserve_new_metadata()`.
- `ocfs2_is_cluster_bitmap()` identifies the global bitmap by comparing the OSB bitmap block number with the inode's disk block number.
- `ocfs2_which_suballoc_group()` assumes a normal contiguous mapping where group block is `block - bit`; callers use `i_suballoc_loc` for discontiguous cases when available.
- The find-then-claim inode APIs are specifically documented as used by `ocfs2_create_inode_in_orphan()`.
