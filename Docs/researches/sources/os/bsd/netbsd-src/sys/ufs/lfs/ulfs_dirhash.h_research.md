# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_dirhash.h

## Scope

Declares the ULFS directory hash data structure, constants, probe-table layout macros, free-space accounting parameters, and public dirhash API.

## APIs And Behavior

- Defines `DIRHASH_EMPTY`, `DIRHASH_DEL`, `DIRALIGN`, `DH_NFSTATS`, scoring constants, and the two-level hash table geometry.
- `DH_ENTRY()` indexes the two-level hash slot array.
- `struct dirhash` stores the lock, hash arrays, per-directory free-space metadata, sequential lookup optimization state, score, list state, and global-list linkage.
- Declares build, lookup, find-free, end-useful, mutation update, truncation, free, check, init, and done functions.

## State And Dependencies

The structure is embedded indirectly through `struct inode->i_dirhash` and coordinated with the global dirhash LRU/score list protected by `ulfsdirhash_lock`. It uses `doff_t`, `kmutex_t`, `TAILQ_ENTRY`, `LFS_DIRHEADER`, and LFS directory sizing constants.

## Risks And Invariants

Callers must respect the split locking model: most fields are protected by `dh_lock`, while list membership is protected by the global dirhash lock. The hash table deliberately keeps utilization low; if mutation makes it too full, the implementation discards the hash and lets it be rebuilt.
