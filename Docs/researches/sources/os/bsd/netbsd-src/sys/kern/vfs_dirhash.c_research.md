# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_dirhash.c

## Purpose
Provides a generic directory-entry hash cache for filesystems: maps directory names to offsets/sizes, tracks freed directory slots, limits global memory use, and exposes dirhash sysctls.

## Main Interfaces
- `dirhash_init`: initializes pools, LRU queue, memory limits, and sysctl nodes.
- `dirhash_get`, `dirhash_put`: allocate/reference and release a directory hash object.
- `dirhash_purge_entries`, `dirhash_purge`: free entries and recycle whole dirhash objects.
- `dirhash_enter`: add a live directory entry keyed by name hash and offset.
- `dirhash_enter_freed`: record free directory space.
- `dirhash_remove`: remove a live entry and convert its slot to free space.
- `dirhash_lookup`: iterate matching name-hash entries.
- `dirhash_lookup_freed`: iterate free entries large enough for a requested size.
- `dirhash_dir_isempty`: report directory emptiness from completed hash state.

## State And Control Flow
Each `struct dirhash` owns hash buckets for live entries and a free-entry list. The global `dirhash_queue` is protected by `dirhashmutex` and used for LRU-style purging under `maxdirhashsize`. Entry allocation uses pools. `dirhash_enter` may purge unreferenced old dirhashes when global memory would exceed the limit, then inserts the new entry. Callers are expected to hold the filesystem/vnode-specific lock protecting the dirhash itself.

## Dependencies And Integration
Uses kernel pools, sysctl, vnode-facing dirhash structures, `hash32_strn`, global physical-memory sizing, and filesystem-provided directory entry metadata.

## Risks And Edge Cases
- `dirhashsize` is global and updated from entry operations; callers must observe the documented locking model.
- Lookup returns internal entry pointers that must not be used after dropping the protecting node lock.
- `dirhash_remove` panics if the expected entry is absent, so filesystem update ordering must keep dirhash state in sync.
- Global memory limiting is best-effort: if purging cannot free enough, insertion still proceeds with available allocation.
- `dirhash_dir_isempty` relies on `DIRH_COMPLETE` and treats directories with only `..` or no entries as empty.

## Filesystem Relevance
High. This is reusable local-filesystem directory lookup/update acceleration infrastructure.
