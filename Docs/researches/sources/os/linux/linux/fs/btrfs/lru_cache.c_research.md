# File Research: sources/os/linux/linux/fs/btrfs/lru_cache.c

This file implements a small generic Btrfs LRU cache built on a maple tree plus per-key linked lists.

Core responsibilities:
- Initialize cache state with optional maximum size.
- Look up entries by 64-bit key plus optional generation.
- Store new entries and evict the least-recently-used entry when a bounded cache is full.
- Remove and free entries.
- Clear all entries.

Key mechanisms:
- The maple tree maps the key value to a `list_head` containing one or more entries.
- `match_entry()` scans the per-key list for exact `key` and `gen` matches.
- `btrfs_lru_cache_lookup()` moves a found entry to the tail of the global LRU list.
- `btrfs_lru_cache_store()` allocates a per-key list head for new keys, handles `-EEXIST` by appending to the existing list, rejects duplicate key/generation pairs, and evicts from the global LRU head if `max_size` is reached.
- `btrfs_lru_cache_remove()` removes both list links, erases and frees an empty per-key head, frees the embedded entry object, and decrements size.
- `btrfs_lru_cache_clear()` walks the LRU list and removes everything.

Important invariants:
- Entries are heap-allocated objects whose first member is `struct btrfs_lru_cache_entry`; removal frees the containing object with `kfree()`.
- Cache users must provide external synchronization if needed; this module does not lock internally.
- The per-key list handles 64-bit keys on 32-bit systems where maple tree keys are only unsigned long width.

Cross-file relationships:
- Public types and iteration helpers are in `lru_cache.h`.
- Uses Btrfs `ASSERT()` from `messages.h`.
