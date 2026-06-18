# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/rrset.c

## Purpose
Implements the RRset cache wrapper around Unbound's slabhash, including insertion/update policy, TTL checks, LRU touch behavior, security-status propagation, wildcard insertion, and selective cache removal.

## Main Responsibilities
- Create/delete/adjust `struct rrset_cache`.
- Safely touch LRU state without holding other RRset locks.
- Merge newly parsed RRsets with cached RRsets according to TTL, trust, security status, data equality, and special NS behavior.
- Lookup RRsets with expiration checks, including a short grace for upstream TTL=0 DNAME synthesis.
- Lock/unlock sorted arrays of RRset references used by message-cache entries.
- Update/check security status when validation improves cached or in-flight RRsets.
- Remove or detect expired parent RRsets above a query name.

## Important Functions
- `rrset_cache_create()`: creates a slabhash using packed-RRset size/compare/delete callbacks and installs `rrset_markdel()`.
- `rrset_cache_touch()`: locks the target slab then entry, verifies id/hash, and touches LRU. Comments explicitly warn callers not to hold any RRset lock.
- `need_to_update_rrset()`: central update policy. Prefers unexpired, secure, non-bogus, and higher-trust data; constrains NS TTL extension to reduce ghost-domain persistence.
- `rrset_cache_update()`: looks up existing data, possibly returns cached superior reference, inserts replacement, and changes IDs for changed NSEC/NSEC3/DNAME data so message-cache proofs are invalidated.
- `rrset_cache_update_wildcard()`: copies an RRset and rewrites owner name to `*.<closest-encloser>`.
- `rrset_cache_lookup()`: builds a stack key, looks up slabhash, and rejects expired data except TTL=0 upstream DNAMEs within `DNAME_TTL0_GRACE_SECONDS`.
- `rrset_array_lock()/unlock()/unlock_touch()`: lock reference arrays once per duplicate key and optionally touch LRU after releasing locks.
- `rrset_update_sec_status()` / `rrset_check_sec_status()`: copy better validation/trust state between a provided RRset and cache entry if rdata still matches.
- `rrset_cache_remove_above()` and `rrset_cache_expired_above()`: walk parent labels to evict or inspect parent RRsets.

## Concurrency and Lifetime
The implementation relies on slabhash and per-entry locks. Inserted RRsets become immutable without holding their entry lock. The cache update path has an acknowledged gap between unlocking an existing entry and inserting replacement data; comments treat races as acceptable cache behavior.

## Edge Cases and Risks
- TTL=0 DNAME grace is intentionally non-RFC caching behavior for immediate synthesis load reduction.
- `rrset_array_unlock_touch()` may skip LRU touches on regional allocation failure but still releases locks.
- NS updates deliberately avoid extending TTL past the cached entry in several cases, preventing stale delegation persistence.
