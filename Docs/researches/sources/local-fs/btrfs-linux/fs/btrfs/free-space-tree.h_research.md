# File Research: sources/local-fs/btrfs-linux/fs/btrfs/free-space-tree.h

## Summary
Declares the public interface and constants for the persistent Btrfs free-space tree.

## Main Contents
- `BTRFS_FREE_SPACE_BITMAP_SIZE` fixed at 256 bytes for default bitmap item payloads.
- `BTRFS_FREE_SPACE_BITMAP_BITS` derived from bitmap size and bits per byte.
- Declarations for free-space tree create/delete/rebuild/load operations.
- Declarations for per-block-group add/remove and per-range add/remove hooks.
- Declarations for info-item lookup and free-space-root selection.
- Additional test-only declarations when `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` is enabled.

## Key Interfaces
Primary callers use `btrfs_add_to_free_space_tree()` and `btrfs_remove_from_free_space_tree()` from allocation/free paths, `btrfs_load_free_space_tree()` from block-group caching, and `btrfs_create_free_space_tree()`, `btrfs_delete_free_space_tree()`, or `btrfs_rebuild_free_space_tree()` from mount or feature-management paths.

## Important Details
The header documents that the final bitmap in a block group may be shorter than the default size and that implementation code must not assume existing bitmap items always have the default payload length.

## Risks
The interface is transaction-oriented. Callers must pass valid transaction handles for mutating operations and must respect feature gating so that free-space tree updates are skipped when the compat-ro feature is not active.
