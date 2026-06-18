# File Research: sources/local-fs/kdave-linux/fs/btrfs/lru_cache.h

## Purpose

`lru_cache.h` defines the data structures and API for Btrfs’s generic LRU cache helper.

## Structures

`struct btrfs_lru_cache_entry` contains:

- `lru_list` for global LRU order.
- `key` as full `u64` logical key.
- `gen` as optional generation discriminator.
- `list` for the per-maple-tree-key bucket.

The header documents two important ownership/layout constraints: the entry must be embedded as the first member of its containing struct, and the allocation must be compatible with `kfree()`.

`struct btrfs_lru_cache` contains the global LRU list, maple tree, current size, and max size.

## APIs

Declared operations:

- `btrfs_lru_cache_init()`
- `btrfs_lru_cache_lookup()`
- `btrfs_lru_cache_store()`
- `btrfs_lru_cache_remove()`
- `btrfs_lru_cache_clear()`

It also provides `btrfs_lru_cache_for_each_entry_safe()` and `btrfs_lru_cache_lru_entry()` helpers.

## Integration Notes

The header abstracts away 32-bit maple-tree key limitations by storing full `u64` keys in entries and allowing bucket lists under a maple-tree slot. Callers must provide external locking if cache access is concurrent.
