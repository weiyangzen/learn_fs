# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_alloc.h

## Purpose

This header declares the XFS allocator API, allocation argument structure, allocator flags, free/deferred-free types, AGFL helpers, and query interfaces.

## Key Types

- `struct xfs_alloc_arg`
  - Carries allocation input and output state through allocator layers.
  - Important fields:
    - transaction, mount, AGF buffer, per-AG pointer
    - target fsblock/AG/AG block
    - min/max length, alignment, mod/prod
    - `minleft`, `total`, and `minalignslop`
    - AG block range for near allocations
    - output length and AG block
    - datatype flags
    - owner info
    - per-AG reservation type
    - `wasdel`, `wasfromfl`, `alloc_minlen_only`
- `struct xfs_extent_free_item`
  - Deferred extent free item with owner, startblock, length, group pointer, flags, and reservation type.
- `struct xfs_alloc_autoreap`
  - Holds paused deferred work for autoreap behavior.

## Flags

- `XFS_ALLOC_FLAG_TRYLOCK`
- `XFS_ALLOC_FLAG_FREEING`
- `XFS_ALLOC_FLAG_NORMAP`
- `XFS_ALLOC_FLAG_NOSHRINK`
- `XFS_ALLOC_FLAG_CHECK`
- `XFS_ALLOC_FLAG_TRYFLUSH`

Datatype flags:

- `XFS_ALLOC_USERDATA`
- `XFS_ALLOC_INITIAL_USER_DATA`
- `XFS_ALLOC_NOBUSY`

Deferred free flags:

- `XFS_FREE_EXTENT_SKIP_DISCARD`
- `XFS_FREE_EXTENT_REALTIME`

EFI flags:

- skip discard
- attr fork
- bmap btree block
- cancelled
- realtime

## Declared API Areas

- AGFL and reservation sizing:
  - `xfs_agfl_size`
  - `xfs_alloc_set_aside`
  - `xfs_alloc_ag_max_usable`
  - `xfs_alloc_min_freelist`
  - `xfs_alloc_longest_free_extent`
- Allocation:
  - `xfs_alloc_vextent_this_ag`
  - `xfs_alloc_vextent_near_bno`
  - `xfs_alloc_vextent_exact_bno`
  - `xfs_alloc_vextent_start_ag`
  - `xfs_alloc_vextent_first_ag`
- Freeing:
  - `__xfs_free_extent`
  - inline `xfs_free_extent`
  - `xfs_free_ag_extent`
  - `xfs_free_extent_later`
  - `xfs_free_extent_fix_freelist`
- Btree helpers:
  - lookup/get record functions
  - record conversion and validation
  - query range/all/has-records
- AGF/AGFL IO and logging:
  - `xfs_read_agf`
  - `xfs_alloc_read_agf`
  - `xfs_alloc_read_agfl`
  - `xfs_alloc_get_freelist`
  - `xfs_alloc_put_freelist`
  - `xfs_alloc_log_agf`
  - `xfs_agfl_walk`
- Autoreap:
  - schedule, cancel, commit
- Cache lifecycle:
  - `xfs_extfree_intent_init_cache`
  - `xfs_extfree_intent_destroy_cache`
- Validation:
  - `xfs_validate_ag_length`

## Important Invariants

- `xfs_buf_to_agfl_bno` abstracts CRC versus non-CRC AGFL layout.
- Realtime deferred frees cannot use AG reservations.
- `xfs_efi_is_realtime` checks EFI realtime flag.
- `XFS_FREE_EXTENT_ALL_FLAGS` defines the accepted mask for deferred free requests.

## Research Notes

This is the allocator contract consumed by bmap, AG grow/shrink, repair/scrub, rmap/refcount, and transaction defer code. `xfs_alloc_arg` is the central context object, so correct initialization of its length, alignment, owner, reservation, and per-AG fields is essential.
