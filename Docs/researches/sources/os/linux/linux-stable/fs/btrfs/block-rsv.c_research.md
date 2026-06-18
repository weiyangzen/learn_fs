# File Research: sources/os/linux/linux-stable/fs/btrfs/block-rsv.c

## Purpose

`block-rsv.c` implements Btrfs metadata block reserves. A block reserve is a logical bucket with desired `size`, current `reserved` bytes, a metadata `space_info`, qgroup metadata reserve mirrors, and policy flags. These reserves allow transaction, delayed refs, delayed items, chunk updates, tree log, global fallback, remap, truncate, and temporary metadata users to reserve pessimistically and then release or migrate unused space safely.

## Block Reserve Model

The file-level comment defines the lifecycle:

- Reserve:
  - `btrfs_block_rsv_add()` and `btrfs_block_rsv_refill()` reserve metadata bytes through `btrfs_reserve_metadata_bytes()`.
  - Reserved bytes are accounted in `space_info->bytes_may_use`.
  - `btrfs_block_rsv_add()` also grows `block_rsv->size`.
- Use:
  - `btrfs_use_block_rsv()` selects the correct reserve and consumes bytes when tree blocks are allocated.
- Finish:
  - `btrfs_block_rsv_release()` shrinks `size`, returns excess `reserved` bytes, and preferentially refills delayed refs or global reserves before freeing to `space_info`.

Reserve types have distinct roles:

- Transaction, delayed operations, and chunk reserves are scoped to specific operations.
- Global reserve is the overflow reserve for extent tree updates and ENOSPC recovery paths such as eviction/truncate.
- Delalloc reserve covers per-inode metadata for file extents, inode updates, and checksums.
- Delayed refs reserve tracks expected delayed-reference metadata demand and is preferentially refilled from excess.
- Empty reserve falls back to on-demand reservation.
- Temp reserve supports unbounded operations such as truncate/iput, with `failfast` allowing work to stop and retry with a new reservation.

## Main APIs And Behavior

- `block_rsv_release_bytes()` is the core release helper:
  - Shrinks `size` by requested bytes or all bytes for `(u64)-1`.
  - Caps `reserved` to `size`.
  - Optionally computes qgroup excess.
  - Moves excess bytes to a destination reserve if it is not full.
  - Frees remaining excess from `space_info->bytes_may_use`.
- `btrfs_block_rsv_migrate()` consumes bytes from a source reserve and adds them to a destination reserve.
- `btrfs_init_block_rsv()` clears and initializes a reserve.
- `btrfs_init_metadata_block_rsv()` initializes a metadata reserve and binds it to metadata `space_info`.
- `btrfs_alloc_block_rsv()` allocates a heap reserve.
- `btrfs_free_block_rsv()` releases all bytes and frees it.
- `btrfs_block_rsv_add()` reserves metadata and grows `size/reserved`.
- `btrfs_block_rsv_check()` checks whether a reserve has at least `min_percent` of its target.
- `btrfs_block_rsv_refill()` only reserves the delta needed to satisfy `num_bytes`.
- `btrfs_block_rsv_release()` chooses the refill target:
  - delayed refs reserve releases excess toward global reserve.
  - most other non-global reserves release excess toward delayed refs if it is not full.
  - cross-`space_info` transfers are disallowed.
- `btrfs_block_rsv_use_bytes()` subtracts reserved bytes or returns `-ENOSPC`.
- `btrfs_block_rsv_add_bytes()` adds already-reserved bytes to a reserve and optionally grows `size`.

## Global And Root Reserve Setup

- `btrfs_update_global_block_rsv()` sizes the global reserve from root usage:
  - Starts with tree root usage.
  - Adds extent, checksum, and free-space tree global roots.
  - Adds block-group root for `BLOCK_GROUP_TREE`.
  - Adds stripe root for `RAID_STRIPE_TREE`.
  - Ensures enough minimum space for unlink metadata and delayed refs.
  - Caps reserve size at 512 MiB.
  - Updates `space_info->bytes_may_use`, grants tickets when shrinking, and may force chunk allocation if reserve size reaches total metadata space.
- `btrfs_init_root_block_rsv()` assigns root-level reserves:
  - extent/checksum/free-space/block-group/raid-stripe roots use delayed refs reserve.
  - root/device/quota roots use global reserve.
  - chunk root uses chunk reserve.
  - tree log uses treelog reserve.
  - remap root uses remap reserve.
  - other roots default to no root reserve.
- `btrfs_init_global_block_rsv()` binds fs-wide reserves to the right `space_info`:
  - chunk reserve uses system space.
  - remap reserve uses metadata-remap space.
  - global/trans/empty/delayed/delayed-refs use metadata space.
  - treelog uses metadata space, or a dedicated zoned treelog subgroup.
  - Then it initializes global reserve sizing.
- `btrfs_release_global_block_rsv()` releases the global reserve and warns if other fs-wide reserves still have size or reserved bytes.

## Reserve Selection And Use

- `get_block_rsv()` chooses a reserve for a tree block allocation:
  - Shareable roots, UUID root, and checksum-tree writes during checksum insertion use the transaction reserve.
  - Otherwise use `root->block_rsv`.
  - Fall back to `empty_block_rsv`.
- `btrfs_use_block_rsv()` consumes one tree block worth of metadata:
  - Tries the selected reserve first.
  - Honors `failfast`.
  - Refreshes global reserve once if using it.
  - Emits ENOSPC debug warnings for most non-delayed-ref failures.
  - Attempts a direct no-flush reservation.
  - Refuses tree-log fallback to global/emergency reserves so fsync can fall back to full transaction commit.
  - May consume from global reserve if same `space_info`.
  - As a last resort, attempts `BTRFS_RESERVE_FLUSH_EMERGENCY`.
- `btrfs_check_trunc_cache_free_space()` verifies a reserve has enough bytes for truncating free-space cache plus inode update.

## Dependencies

- Space-info accounting:
  - `btrfs_reserve_metadata_bytes()`
  - `btrfs_space_info_free_bytes_may_use()`
  - `btrfs_space_info_update_bytes_may_use()`
  - `btrfs_try_granting_tickets()`
- Root/tree accounting:
  - `btrfs_root_used()`
  - `btrfs_calc_insert_metadata_size()`
  - `btrfs_calc_metadata_size()`
  - `btrfs_calc_delayed_ref_bytes()`
- Filesystem feature checks:
  - block-group tree
  - RAID stripe tree
  - zoned mode
- Transaction/root identity is needed to choose reserves safely.

## Risks And Invariants

- `size` and `reserved` must be changed under `block_rsv->lock`.
- Releasing bytes must not transfer reserves across different `space_info` objects.
- The global reserve is deliberately protected from tree-log allocations; consuming it for fsync log trees can increase transaction-abort risk.
- `failfast` is critical for truncate/temp reserves because those operations are unbounded and must be able to stop, commit/re-reserve, and continue.
- Global reserve sizing must include roots introduced by optional features, or ENOSPC handling can under-reserve metadata required to finish commits.
- Qgroup reserve fields mirror but do not exactly match normal metadata reserve semantics; callers must release qgroup excess through the provided output when needed.
