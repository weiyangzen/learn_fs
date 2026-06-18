# File Research: sources/local-fs/btrfs-linux/fs/btrfs/lru_cache.h

## Purpose

Defines the generic LRU cache structures and API.

## Main Contents

- `struct btrfs_lru_cache_entry`, intended to be embedded as the first member of caller-owned structures.
- `struct btrfs_lru_cache`, containing the LRU list, maple tree, current size, and max size.
- Safe reverse iteration macro and helper for current LRU entry.
- Init, lookup, store, remove, and clear prototypes.

## Key Contract

The entry must be first in its containing allocation and allocated with `kmalloc()` semantics because cache removal calls `kfree()` on the entry pointer.
