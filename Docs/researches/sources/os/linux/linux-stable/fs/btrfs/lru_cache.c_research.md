# File Research: sources/os/linux/linux-stable/fs/btrfs/lru_cache.c

## Summary
Implements a small generic Btrfs LRU cache backed by a maple tree and per-key linked lists.

## Main Responsibilities
- Initializes bounded or unbounded cache objects.
- Looks up entries by 64-bit key and generation.
- Stores new entries, rejecting duplicate key/generation pairs.
- Evicts the least recently used entry when `max_size` is reached.
- Removes individual entries and clears the cache.

## Key APIs
- `btrfs_lru_cache_init()`.
- `btrfs_lru_cache_lookup()`.
- `btrfs_lru_cache_store()`.
- `btrfs_lru_cache_remove()`.
- `btrfs_lru_cache_clear()`.

## Important Behavior
The maple tree maps the key to a heap-allocated list head. Each list contains entries with the same maple-tree key value. This supports full `u64` keys even on 32-bit systems, where maple tree keys are only `unsigned long`.

Lookup moves a found entry to the tail of the LRU list. Store inserts a new per-key list head when needed or appends to an existing list. If the cache is full, store removes and frees the current least-recently-used entry before linking the new entry.

Removal deletes the entry from both the per-key list and the LRU list. If the per-key list becomes empty, the list head is erased from the maple tree and freed. Entries are freed with `kfree()`.

## State and Synchronization
No internal locking is provided. Callers must serialize cache access. Cache size is updated after successful store/remove operations.

## Risks
Entries must be kmalloc-backed and embed `struct btrfs_lru_cache_entry` at offset zero, because the cache frees entries directly. Duplicate store returns `-EEXIST` after freeing only the temporary list head, not the caller-supplied entry.
