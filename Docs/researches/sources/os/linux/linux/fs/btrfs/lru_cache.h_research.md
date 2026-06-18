# File Research: sources/os/linux/linux/fs/btrfs/lru_cache.h

This header defines the generic Btrfs LRU cache entry and cache container.

Key structures:
- `struct btrfs_lru_cache_entry` is intended to be embedded at offset zero in a caller-owned object. It stores global LRU linkage, 64-bit key, optional generation, and per-key list linkage.
- `struct btrfs_lru_cache` stores the global LRU list, maple tree of key-to-list mappings, current size, and maximum size.

Exported API:
- `btrfs_lru_cache_init()`
- `btrfs_lru_cache_lookup()`
- `btrfs_lru_cache_store()`
- `btrfs_lru_cache_remove()`
- `btrfs_lru_cache_clear()`

Helpers:
- `btrfs_lru_cache_for_each_entry_safe()` iterates entries from most-recent side safely.
- `btrfs_lru_cache_lru_entry()` returns the least recently used entry or NULL.

Design notes:
- The optional generation allows multiple entries for the same key when callers need versioned cache records.
- The key is stored inside the entry to preserve full 64-bit identity even on 32-bit maple-tree key platforms.
