# File Research: sources/local-fs/btrfs-linux/fs/btrfs/lru_cache.c

## Purpose

Implements a small generic Btrfs LRU cache built on a maple tree from key to collision/generation lists plus a global LRU list.

## Main Responsibilities

- Initializes cache state and maximum size.
- Looks up entries by `u64 key` and generation, moving hits to the LRU tail.
- Stores entries, handling maple-tree insertion, same-key generation lists, duplicate detection, and max-size eviction.
- Removes entries, including cleanup of now-empty per-key list heads.
- Clears all entries.

## Key Behaviors and Invariants

- Entries are freed by the cache on removal, so callers must allocate them compatibly with `kfree()`.
- `max_size == 0` means unlimited; caller is then responsible for trimming.
- Same key with different generation is represented by a linked list, mainly for 32-bit maple-tree key truncation and low-collision use cases.
- Eviction removes the least-recently-used entry before adding the new one when the cache is full.
