# sources/user-network-fs/nfs-ganesha/src/support/netgroup_cache.c

## Purpose
This file implements a process-local cache for `innetgr(group, host, NULL, NULL)` lookups. It caches both positive and negative netgroup membership answers to reduce NSS/SSSD lookup cost in export/client matching paths.

## Important APIs, Types, And Functions
`struct ng_cache_info` stores an AVL node, group and host buffer descriptors, and the insertion epoch. Public entry points are `ng_cache_init`, `ng_cache_cleanup`, `ng_innetgr`, and `ng_clear_cache`. Internal helpers include `ng_hash_key`, `buffdesc_comparator`, `ng_comparator`, `ng_expired`, `ng_free`, `ng_remove`, `ng_add`, and `ng_lookup`. A global `pthread_rwlock_t ng_lock` protects the AVL trees.

## Control Flow
Initialization creates separate positive and negative AVL trees and clears a small positive direct-mapped hash array. `ng_innetgr` first takes the read lock, checks the positive tree/cache, then the negative tree. On a double miss, it takes the write lock, calls `innetgr`, stores the result into the positive or negative cache, and returns the result. Expired entries are detected during lookup; lookup temporarily drops the read lock, reacquires the write lock, confirms the node still exists, removes and frees it, then resumes with a read lock and reports a miss.

## State And Persistence
State is in memory only: `pos_ng_tree`, `neg_ng_tree`, `ng_cache[1009]`, and the lock. Entries expire after a hard-coded 30 minutes. There is no disk persistence; cache contents are wiped by `ng_clear_cache` or process shutdown cleanup.

## Dependencies And Integration Points
The code uses Ganesha AVL, buffer, memory, atomic pointer, logging, cleanup, and config support plus libc `innetgr`. It integrates with export access control and idmapping/client matching code that asks whether a client host belongs to a configured netgroup.

## Risks And Test Signals
Risks include stale authorization for up to 30 minutes, no configurable TTL in this file, direct-mapped positive cache collisions replacing `ng_cache` slots, possible duplicate lookups while the read lock is dropped for expiry removal, and reliance on serialized `innetgr` calls because SSSD behavior is noted as unsafe under parallel calls. Tests should exercise positive and negative hits, expiry, duplicate inserts, `ng_clear_cache`, concurrent readers with expiry, hash collision fallback to AVL lookup, and SSSD/NSS failure behavior.
