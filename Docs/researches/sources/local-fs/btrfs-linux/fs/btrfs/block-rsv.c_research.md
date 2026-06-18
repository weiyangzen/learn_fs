# File Research: sources/local-fs/btrfs-linux/fs/btrfs/block-rsv.c

## Scope

This file implements Btrfs metadata block reserves, which are logical buckets for metadata reservations. It handles reserve initialization, reservation/refill/release, migration between reserves, use during tree block allocation, global reserve sizing, root-to-reserve assignment, and fallback behavior when a reserve is short.

## Main APIs And Entry Points

- `btrfs_init_block_rsv()` initializes a reserve with lock and type.
- `btrfs_init_metadata_block_rsv()` initializes a reserve and attaches it to metadata `space_info`.
- `btrfs_alloc_block_rsv()` and `btrfs_free_block_rsv()` allocate/free dynamic reserves and release all held bytes.
- `btrfs_block_rsv_add()` reserves metadata bytes from `space_info` and adds them to reserve size and reserved counters.
- `btrfs_block_rsv_refill()` reserves only the gap needed to reach a requested reserved byte count.
- `btrfs_block_rsv_release()` releases bytes from a reserve, optionally returning excess to delayed-ref or global reserves before freeing bytes to `space_info->bytes_may_use`.
- `btrfs_block_rsv_migrate()` consumes bytes from one reserve and adds them to another.
- `btrfs_block_rsv_use_bytes()` consumes reserved bytes for a tree-block allocation.
- `btrfs_block_rsv_add_bytes()` credits bytes directly to a reserve.
- `btrfs_update_global_block_rsv()` sizes and fills the global reserve from root-tree, extent-tree, checksum-tree, free-space-tree, block-group-tree, stripe-tree, and unlink fallback needs.
- `btrfs_init_root_block_rsv()` assigns each root to the reserve appropriate for its tree type.
- `btrfs_init_global_block_rsv()` attaches fs-wide reserves to their space-info objects and initializes the global reserve.
- `btrfs_release_global_block_rsv()` drains global reserves during teardown and warns on leaked reserve state.
- `btrfs_use_block_rsv()` selects and consumes the reserve to use for COW/tree block allocation, with fallback to direct reservation, global reserve, or emergency reservation.
- `btrfs_check_trunc_cache_free_space()` verifies that a reserve has enough bytes to safely truncate a free-space cache inode.

## Reserve Model

Each `struct btrfs_block_rsv` has:

- `size`: target logical reservation size.
- `reserved`: currently reserved metadata bytes.
- `space_info`: the metadata/system/remap pool backing the reserve.
- `full`: fast-path fullness indicator.
- `failfast`: used by bounded temporary operations such as truncate/iput.
- `type`: reserve category.
- `qgroup_rsv_size` and `qgroup_rsv_reserved`: quota-group metadata reservation analogues.

The file documents the intended behavior of reserve types:

- Transaction, delayed ops, and chunk reserves behave as normal scoped reservations.
- Global reserve is a safety buffer for under-estimated delayed refs and special ENOSPC recovery paths.
- Delalloc reserve is calculated per inode and backs inode/file-extent/csum metadata updates.
- Delayed refs reserve tracks dynamic delayed-ref work and is the preferred sink for excess returned by other reserves.
- Empty reserve is a fallback for operations without a dedicated bucket.
- Temp reserve is used for unbounded operations that perform work until space runs out, then retry with a new reservation.

## Control Flow And Behavior

`block_rsv_release_bytes()` is the core release helper. It subtracts from reserve `size`, clamps `reserved` down to `size`, marks the reserve full when appropriate, computes qgroup excess, optionally tops up a destination reserve, and frees remaining bytes from `space_info->bytes_may_use`.

`btrfs_block_rsv_release()` chooses a destination for excess bytes. Delayed refs release to the global reserve. Other non-global reserves release to the delayed refs reserve if it is not full and uses the same `space_info`. Otherwise excess returns to the space-info pool.

`btrfs_use_block_rsv()` first chooses a reserve with `get_block_rsv()`. Shareable roots, UUID root updates, and csum-tree updates while adding checksums use the transaction reserve. Otherwise the root's assigned reserve is used, falling back to the empty reserve. If the reserve has enough bytes, it consumes them. If not, `failfast` reserves return immediately; global reserve shortage triggers a global reserve recomputation once; non-delayed-ref shortages can warn under ENOSPC debug.

If the selected reserve is short, `btrfs_use_block_rsv()` tries a direct no-flush metadata reservation. Log-tree allocations fail after this point rather than consuming global reserve, forcing fsync to fall back to full transaction commit. Non-global metadata reserves can then borrow from the global reserve if they share the same `space_info`. As a last resort, the function attempts an emergency flush reservation.

`btrfs_update_global_block_rsv()` computes global reserve size from global root usage, selected global roots, optional block-group and RAID stripe roots, plus unlink and delayed-ref fallback items. It caps the reserve at 512 MiB, updates `bytes_may_use` under `space_info->lock`, and can force a metadata chunk allocation if the global reserve size reaches total metadata bytes.

Root reserve assignment is policy-driven. Extent, checksum, free-space, block-group, and RAID stripe roots use delayed refs reserve. Root, device, and quota roots use global reserve. Chunk root uses chunk reserve. Tree log uses treelog reserve. Remap tree uses remap reserve. Other roots default to no root reserve.

## Dependencies

- Space-info metadata reservation and ticket granting.
- Transaction handles and `trans->block_rsv`.
- Root types and feature flags such as block-group tree and RAID stripe tree.
- Delayed refs and unlink metadata sizing helpers.
- Zoned mode special treelog reserve subgroup.
- Metadata sizing helpers for inserts, updates, and delayed refs.

## Risks And Invariants

- Reserve `size` and `reserved` are protected by the reserve spinlock; space-info counter changes require `space_info->lock`.
- Excess release must not move bytes between reserves with different `space_info`.
- Tree-log allocations intentionally avoid global reserve fallback to keep fsync optimization from consuming emergency metadata.
- Global reserve recalculation must include all global roots that can be touched during delayed refs or commit work.
- `btrfs_release_global_block_rsv()` warnings are leak detectors for reserve accounting.
- `failfast` temp reserves rely on callers handling `-ENOSPC` by unwinding and retrying with a fresh reservation.
