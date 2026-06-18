# File Research: sources/local-fs/kdave-linux/fs/btrfs/lru_cache.c

## Purpose

`lru_cache.c` implements a small generic Btrfs LRU cache using a maple tree for key lookup and a list for LRU ordering. It is designed for embedded cache-entry structs whose first field is `struct btrfs_lru_cache_entry`.

## Major Behavior

`btrfs_lru_cache_init()` initializes the LRU list, maple tree, current size, and max size. `max_size == 0` means unlimited size, leaving trimming to the caller.

Lookup uses `mtree_load()` by key, then `match_entry()` scans the per-key list for exact `key` and `gen`. A hit moves the entry to the tail of the LRU list.

Store allocates a list head for a new maple-tree bucket. If the key is new, it inserts the bucket and adds the entry. If the key exists, it frees the unused bucket, loads the existing list, rejects duplicate `(key, gen)` pairs with `-EEXIST`, and appends the new entry. If the cache is full, it evicts the first LRU entry before adding the new one.

Remove deletes the entry from both its per-key list and global LRU list. If the per-key list becomes empty, it erases and frees the maple-tree bucket. Removal frees the entry itself and decrements size.

Clear iterates the LRU list and removes every entry, then asserts an empty cache and maple tree.

## Dependencies and Integration

Depends on Linux maple tree, list APIs, `kmalloc_obj`, `kfree`, and Btrfs `ASSERT()`. The caller is responsible for synchronization; no internal lock protects the cache.

## Risk Notes

The cache assumes entries are kmalloc-backed and that `struct btrfs_lru_cache_entry` is at offset 0 in the embedding allocation. Violating either assumption would make eviction/freeing unsafe. The per-key list handles 32-bit maple key truncation scenarios and same-key generations.
