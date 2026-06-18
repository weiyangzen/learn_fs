# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_dirhash.c

## Scope

Implements the ULFS directory hash cache used by LFS for fast large-directory lookup, free-space discovery, directory mutation updates, memory recycling, sanity checking, sysctls, and lifecycle management.

## APIs And Behavior

- `ulfsdirhash_build()` decides whether a directory merits hashing, reserves global dirhash memory, allocates two-level hash and per-block free-space tables, scans every directory entry, inserts live names, and records free space.
- `ulfsdirhash_free()` detaches a directory hash from its inode/list, releases hash arrays and block-free metadata, and updates global memory accounting.
- `ulfsdirhash_lookup()` probes by name, optionally optimizes sequential lookup, validates directory entries from buffers, returns entry offset/buffer and previous offset, or asks callers to fall back to linear search.
- `ulfsdirhash_findfree()` finds a directory block with enough compactable free space; `ulfsdirhash_enduseful()` finds trailing fully free directory space.
- `ulfsdirhash_add()`, `ulfsdirhash_remove()`, `ulfsdirhash_move()`, `ulfsdirhash_newblk()`, and `ulfsdirhash_dirtrunc()` update hash slots and block-free summaries after directory mutations.
- `ulfsdirhash_checkblock()` optionally verifies that a directory block matches the hash and free-space summaries.
- Static helpers hash names, adjust free summaries, find/delete probe slots, find previous entries, and recycle low-score hashes to stay under the memory cap.
- `ulfsdirhash_init()` sets default memory limits, initializes locks/pool caches/sysctls, and `ulfsdirhash_done()` tears them down.

## State And Dependencies

Global state includes `ulfsdirhash_list`, `ulfsdirhash_lock`, memory usage/cap sysctls, and pool caches. Per-directory `struct dirhash` state includes two-level probe tables, free-space summaries, first-free indexes, sequential lookup state, score, list membership, and `dh_lock`. It depends on LFS directory accessors, ULFS block reads, vnode/inode state, hash32, kmem, pools, atomics, and sysctl.

## Risks And Invariants

The hash uses open addressing with `DIRHASH_DEL`, so deletion compaction must preserve probe chains. Memory recycling can detach hash storage asynchronously by setting `dh_hash` to `NULL`; users must detect that and fall back/rebuild. Free-space indexes must match actual directory entries or creation/truncation decisions become unsafe. Old-format directories are excluded from hashing.
