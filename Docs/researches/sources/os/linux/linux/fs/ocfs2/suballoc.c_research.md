# File Research: sources/os/linux/linux/fs/ocfs2/suballoc.c

## Purpose

`suballoc.c` implements OCFS2 suballocator mechanics: metadata block allocation, inode allocation, cluster allocation through local/global bitmaps, block group creation and growth, suballocator frees, empty group reclaim, and helper checks for allocated inode bits. It is the core allocator for OCFS2 metadata and data-space bitmap management.

## Core Concepts

- Chain allocator dinodes contain `struct ocfs2_chain_list` records.
- Each chain points to group descriptors (`struct ocfs2_group_desc`) containing allocation bitmaps.
- Metadata and inode allocators are per-slot system inodes and can steal from other node slots under pressure.
- The global cluster bitmap allocates file data clusters and can be assisted by local allocation.
- Block groups can be contiguous or discontiguous when the filesystem supports discontiguous block groups.

`struct ocfs2_suballoc_result` carries allocation search results:

- Group descriptor block (`sr_bg_blkno`) and stable descriptor block (`sr_bg_stable_blkno`).
- First allocated block (`sr_blkno`) for metadata/inode allocations.
- Bitmap offset, number of bits claimed, and max contiguous-free hint.

## Alloc Context Lifetime

`ocfs2_alloc_context` resources are owned through:

- `ocfs2_free_ac_resource()`: unlocks allocator inode, drops bh, clears reservation/find-location private data.
- `ocfs2_free_alloc_context()`: frees resources then the context.

Allocator reservation functions populate:

- `ac_inode`: locked system allocator inode.
- `ac_bh`: locked allocator dinode buffer.
- `ac_bits_wanted` / `ac_bits_given`.
- `ac_which`: local, main, inode, meta, or main-discontiguous allocator mode.
- `ac_group_search`: group search strategy.

## Group Descriptor Validation

Validation is split into:

- `ocfs2_validate_gd_self()`:
  - Signature, `bg_blkno`, generation, free count, bitmap size, and discontiguous extent list bounds.
- `ocfs2_validate_gd_parent()`:
  - Parent dinode pointer, group bit count relative to parent chain geometry, and chain index bounds.
- `ocfs2_validate_group_descriptor()`:
  - ECC validation plus self-validation; parent validation is done by readers that know the parent.
- `ocfs2_check_group_descriptor()`:
  - Resize-oriented version that logs errors rather than taking the filesystem down.

`ocfs2_read_hint_group_descriptor()` handles a stale hint: if the hinted group no longer has a valid group descriptor signature, it removes the buffer from the metadata cache, reports `released=1`, and lets the caller continue with a full chain search.

## Block Group Creation and Growth

`ocfs2_block_group_fill()` initializes a new group descriptor:

- Sets signature, generation, bitmap size, chain id, parent dinode, self block number, and first descriptor bit.
- For full contiguous groups, sets `bg_bits` directly.
- For shorter/discontiguous groups, adds extent records through `ocfs2_bg_discontig_add_extent()`.

Group allocation paths:

- `ocfs2_block_group_alloc_contig()` claims one contiguous cluster run, gets the descriptor block, marks it uptodate, and fills it.
- `ocfs2_block_group_alloc_discontig()` claims an initial region, fills the group, then grows it with additional extent records through `ocfs2_block_group_grow_discontig()`.
- `ocfs2_bg_alloc_cleanup()` frees clusters and removes the descriptor from cache if discontiguous group creation fails.
- `ocfs2_block_group_alloc()` reserves clusters, starts a transaction, creates the group, links it into the allocator chain, updates dinode usage/size/cluster counts, and records `last_alloc_group`.

## Reservation Paths

`ocfs2_reserve_suballoc_bits()` locks a system allocator inode and ensures enough free bits exist. For non-cluster bitmaps it may grow the allocator by allocating a new block group.

Public reservation APIs:

- `ocfs2_reserve_new_metadata_blocks()`: reserves extent allocator bits, first using local slot, then stealing from other slots if needed.
- `ocfs2_reserve_new_metadata()`: computes metadata need from an extent list root.
- `ocfs2_reserve_new_inode()`: reserves one inode bit, respects `inode64` by limiting max block when disabled, and supports inode stealing.
- `ocfs2_reserve_cluster_bitmap_bits()`: reserves bits from the global cluster bitmap.
- `ocfs2_reserve_clusters()`: chooses local allocation when appropriate, otherwise global bitmap; may free truncate-log space and retry.

Steal-slot state:

- `ocfs2_init_steal_slots()` initializes inode/meta steal slots and counters.
- A successful steal records the donor slot and continues stealing up to `OCFS2_MAX_TO_STEAL` before trying the local slot again.

## Allocation Search

Bitmap search and updates:

- `ocfs2_test_bg_bit_allocatable()` avoids reusing bits that are free in memory but still allocated in JBD2 committed data.
- `ocfs2_find_max_contig_free_bits()` scans a bitmap for the largest free run.
- `ocfs2_block_group_find_clear_bits()` finds the best available run in a group.
- `ocfs2_block_group_set_bits()` journals and sets bits, updates free count and contiguous-free hints.

Group search variants:

- `ocfs2_cluster_group_search()` searches cluster bitmaps with `min_bits`, `max_block`, tail-group safety for failed resize, and contig-free hints.
- `ocfs2_block_group_search()` searches metadata/inode block groups, where `min_bits` must be 1.

Chain search:

- `ocfs2_find_victim_chain()` chooses the chain with the most free bits.
- `ocfs2_search_one_group()` tries a specific hinted group.
- `ocfs2_search_chain()` walks a chain and may relink a reasonably empty group to the head to speed future searches.
- `ocfs2_claim_suballoc_bits()` tries last-group hint, then victim chain, then other chains, and falls back to discontiguous main bitmap mode when contiguous cluster allocation fails.

## Public Claim APIs

- `ocfs2_claim_metadata()` claims metadata blocks and returns suballocator location, bit start, block start, and number of bits.
- `ocfs2_find_new_inode_loc()` searches for an inode location without setting allocation bits, used for reflink/orphan ordering.
- `ocfs2_claim_new_inode_at_loc()` later claims the pre-found inode bit and verifies the block number is unchanged.
- `ocfs2_claim_new_inode()` combines search and allocation for ordinary inode allocation.
- `__ocfs2_claim_clusters()` claims data clusters from local allocation or global bitmap, with min/max cluster controls.
- `ocfs2_claim_clusters()` claims remaining reserved cluster bits.

## Free and Reclaim Paths

- `ocfs2_block_group_clear_bits()` journals and clears allocation bits, updates free counts, updates undo buffers for cluster bitmap frees, and refreshes contiguous-free hints.
- `_ocfs2_free_suballoc_bits()` clears bits in a metadata/inode/global bitmap allocator, updates parent chain record and dinode used count, and may reclaim a fully empty non-first suballocator group back to the global bitmap.
- `_ocfs2_reclaim_suballoc_to_main()` removes an empty suballocator group from its chain accounting and frees its clusters into the main global bitmap.
- `ocfs2_free_suballoc_bits()` wraps metadata/inode free without undo handling.
- `ocfs2_free_dinode()` computes an inode's allocator group from `i_suballoc_loc` or block/bit and frees one bit.
- `ocfs2_free_clusters()` frees previously used data clusters with undo protection.
- `ocfs2_release_clusters()` releases never-used clusters without protecting old allocations in the undo buffer.

## Allocator Lock Coordination

`ocfs2_lock_allocators()` decides whether metadata and/or data allocators must be reserved for extent operations:

- It checks free extent records in the destination extent tree.
- Sparse filesystems reserve metadata more conservatively because allocation happens while a journal handle is open.
- It reserves data clusters only when `clusters_to_add` is nonzero.
- On error, it frees any metadata allocation context it created.

## Inode Bit Testing

`ocfs2_test_inode_bit()`:

- Reads the target inode block directly to discover `i_suballoc_slot`, `i_suballoc_loc`, and `i_suballoc_bit`.
- Locks the corresponding inode allocator system inode.
- Reads the group descriptor, tolerating stale released groups as `-ESTALE`.
- Tests the relevant bitmap bit.

This is used by paths that need to verify whether an inode block is still allocated, with comments noting that callers must coordinate with `nfs_sync_lock` to avoid concurrent delete races.

## Correctness Notes

- Group descriptor validation distinguishes fatal normal reads from resize checks that should not force readonly.
- Cluster bitmap allocations use JBD2 undo access to avoid crash windows where recently freed data could be reallocated before transaction commit.
- Many `BUG_ON()` assertions reflect assumptions guaranteed by caller-held locks and prior validation.
- Discontiguous group handling carefully fixes allocation results because bitmap offsets may map into non-contiguous extent records.
- Empty suballocator reclaim intentionally skips the first chain record and non-empty records.
- One suspicious expression in `_ocfs2_reclaim_suballoc_to_main()` subtracts the new on-disk `fe->i_clusters` from `OCFS2_I(alloc_inode)->ip_clusters` after already reducing `fe->i_clusters`; this is worth checking against upstream history if allocator reclaim bugs are being investigated.
