# File Research: sources/os/linux/linux-stable/fs/btrfs/lru_cache.h

## Summary
Defines the generic Btrfs LRU cache data structures and public API.

## Main Contents
- `struct btrfs_lru_cache_entry`.
- `struct btrfs_lru_cache`.
- Safe reverse LRU iteration macro.
- Helper for retrieving the least-recently-used entry.
- Function declarations for init, lookup, store, remove, and clear.

## Important Details
`btrfs_lru_cache_entry` contains both LRU linkage and per-key list linkage. The header documents that it must be embedded as the first member of a kmalloc-allocated owner structure.

`gen` is an optional secondary discriminator for entries sharing a key. The comments caution that many generations per key are stored as a linked list and should remain small.

## Risks
The offset-zero and kmalloc ownership requirements are part of the ABI between this helper and its users. Violating them causes invalid frees or corrupted container interpretation.
