# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_acache.c

## Purpose

`nfs4_acache.c` implements the NFSv4 client access cache. It stores ACCESS results per `(rnode4_t, credential)` so repeated access checks can avoid unnecessary NFSv4 server calls when cached attributes are still valid.

This is a small, focused file. It owns the NFSv4 access-cache hash table, allocation cache, lookup/update logic, per-rnode purge, and module init/fini routines.

## Main Interfaces

Public functions:

- `nfs4_access_check(rnode4_t *rp, uint32_t acc, cred_t *cr)`
- `nfs4_access_cache(rnode4_t *rp, uint32_t acc, uint32_t resacc, cred_t *cr)`
- `nfs4_access_purge_rp(rnode4_t *rp)`
- `nfs4_acache_init(void)`
- `nfs4_acache_fini(void)`

Private helper:

- `acache4hash(rnode4_t *rp, cred_t *cred)`

## Data Structures

The global cache state is:

- `acache4`: array of hash buckets
- `nacache`: optional sizing override
- `acache4size` and `acache4mask`: power-of-two hash sizing and mask
- `acache4_cache`: `kmem_cache` for `acache4_t`
- `acache4_hashlen`: target average chain length
- `ACACHE4_SHIFT_BITS`: shifts rnode pointer bits before hashing, to avoid allocation-alignment noise

Each cache entry records:

- `known`: access bits for which the cache has an answer
- `allowed`: access bits allowed by the server
- `rnode`: owning NFSv4 rnode
- `cred`: held credential
- hash queue links
- per-rnode list link

The same entry is linked both into a global hash bucket and into `rp->r_acache`, enabling efficient lookup by hash and efficient purge by rnode.

## Lookup Behavior

`nfs4_access_check()` first refuses to use the cache if the vnode attribute cache is invalid or if a purge is pending/completing:

- `ATTRCACHE4_VALID(vp)` must be true.
- `nfs4_waitfor_purge_complete(vp)` must not require waiting/fail use.

If an access cache exists for the rnode, the function locks the relevant hash bucket as reader, searches for an entry whose credential compares equal with `crcmp()` and whose `rnode` matches, then returns:

- `NFS4_ACCESS_ALLOWED` when all requested bits are known and allowed.
- `NFS4_ACCESS_DENIED` when all requested bits are known but not all allowed.
- `NFS4_ACCESS_UNKNOWN` when no entry exists or requested bits are not fully known.

Debug counters track hits and misses.

## Update Behavior

`nfs4_access_cache()` records a server ACCESS answer. It preallocates a new cache entry with `KM_NOSLEEP` before taking the bucket writer lock. This avoids sleeping while holding the hash lock.

If an entry already exists for the same rnode and credential, it merges the new knowledge:

- `known |= acc`
- clears the newly checked bits from `allowed`
- applies `resacc` for the checked bits

If no entry exists and allocation succeeded, it inserts the entry into the hash bucket and links it into `rp->r_acache` under `r_statelock`. The credential is held with `crhold()` and later released during purge.

If allocation fails, the function silently skips caching; correctness falls back to future server ACCESS calls.

## Purge Behavior

`nfs4_access_purge_rp()` removes all access-cache entries for one rnode. It first detaches the per-rnode list under `r_statelock`, then iterates that detached list. For each entry, it takes the entry's hash bucket writer lock, unlinks the hash queue links, releases the credential, and frees the entry from `acache4_cache`.

This two-index design avoids a full global hash scan during rnode invalidation.

## Initialization And Finalization

`nfs4_acache_init()` sizes the hash table from `nacache` if set, otherwise from external `rtable4size`. It initializes each bucket as a circular doubly linked list with an `rwlock`, then creates the `nfs4_access_cache` kmem cache.

`nfs4_acache_fini()` destroys the kmem cache, destroys each bucket lock, and frees the hash table.

## Concurrency And Invariants

- Hash buckets use reader/writer locks.
- The per-rnode `r_acache` pointer is protected by `rp->r_statelock`.
- Entries are linked in both hash and rnode lists.
- Cached answers are only trusted while attribute cache state is valid.
- Credentials are reference-counted for the lifetime of cache entries.
- The code assumes cache finalization occurs after entries have been purged; `nfs4_acache_fini()` destroys the object cache directly.

## Dependencies

This file depends on:

- NFSv4 rnode/vnode conversion via `RTOV4()`.
- Attribute-cache validity macros and purge synchronization.
- Credential comparison and reference management: `crcmp`, `crhold`, `crfree`, `crgetuid`.
- illumos kernel allocation and synchronization primitives: `kmem_alloc`, `kmem_cache_*`, `rw_enter`, `rw_exit`, `mutex_enter`.

## Research Notes

The important behavior is the coupling between access-cache validity and attribute-cache validity. Access results are permission snapshots and are only safe while file attributes and purge state are current. Audit focus should be on purge ordering, dual-list unlink correctness, hash sizing, and callers ensuring `nfs4_access_purge_rp()` runs on permission-changing attribute updates.
