# sources/user-network-fs/nfs-ganesha/src/FSAL/Stackable_FSALs/FSAL_MDCACHE/mdcache_hash.h

## Purpose

This header defines MDCACHE's hashed file-handle index. It provides partition types, key hashing, latch locking, fast lookup through cache slots, AVL comparison, insertion, and removal helpers for `mdcache_entry_t`. The source was read as a complete 461-line file.

## Important APIs, Types, and Functions

Core types are `cih_partition_t`, `struct cih_lookup_table`, and `cih_latch_t`. Important APIs/macros include `cih_partition_of_scalar`, `cih_cache_offsetof`, `cih_fh_cmpf`, `cih_fhcache_inline_lookup`, `cih_hash_key`, `cih_hash_release`, `cih_latch_entry`, `cih_get_by_key_latch`, `cih_set_latched`, `cih_remove_checked`, and `cih_remove_latched`. Flags include `CIH_HASH_KEY_PROTOTYPE`, `CIH_GET_UNLOCK_ON_MISS`, `CIH_SET_HASHED`, `CIH_SET_UNLOCK`, and `CIH_REMOVE_UNLOCK`.

## Control Flow

Callers hash a key using CityHash, select a partition by hash modulo partition count, and latch that partition mutex. Lookup first probes the cache slot indexed by hash modulo cache size, validates with `mdcache_key_cmp`, then falls back to the AVL tree and updates the slot on hit. Insert places the entry into the latched partition AVL and sets `inavl`. Removal clears AVL membership and the cache slot, then drops the sentinel LRU ref outside or as part of the locked path depending on helper used.

## State and Persistence Behavior

The header manipulates in-memory hash keys, AVL nodes, `inavl` flags, partition cache slots, and LRU sentinel refs. It intentionally refuses to return entries whose LRU refcount is already zero.

## Dependencies and Integration Points

It integrates with `mdcache_int.h`, `mdcache_lru.h`, `abstract_atomic`, CityHash, AVL trees, lock tracing, and optional LTTng tracepoints. `mdcache_hash.c` provides the global table storage and lifecycle.

## Risks and Edge Cases

Partition locks must not be held while dropping the last LRU ref in paths that can recurse into hash removal. Cache slots are optimistic and must always be validated. Key prototype usage borrows caller buffer storage, so lifetime must cover lookup. Incorrect hash/key duplication leaks or corrupts cache lookup.

## Test Signals

Concurrent lookup/insert/remove stress, cache-slot hit/miss correctness, duplicate key comparison, zero-ref entry rejection, locktrace builds, LTTng trace compile coverage, and sentinel-ref release behavior under final unref.
