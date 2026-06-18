# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/services/cache/rrset.h

## Purpose
Declares the RRset cache API used by Unbound's resolver and message-cache layers.

## Key Type
- `struct rrset_cache`: a thin wrapper whose first member is `struct slabhash table`, allowing slabhash lifecycle functions to manage the allocated object.

## API Surface
- Lifecycle: `rrset_cache_create()`, `rrset_cache_delete()`, `rrset_cache_adjust()`.
- LRU/cache updates: `rrset_cache_touch()`, `rrset_cache_update()`, `rrset_cache_update_wildcard()`.
- Lookup: `rrset_cache_lookup()` returns a locked packed RRset or `NULL`.
- Reference-array locking: `rrset_array_lock()`, `rrset_array_unlock()`, `rrset_array_unlock_touch()`.
- Validation status: `rrset_update_sec_status()`, `rrset_check_sec_status()`.
- Parent cleanup/inspection: `rrset_cache_remove_above()`, `rrset_cache_expired_above()`.
- Direct removal and deletion marking: `rrset_cache_remove()`, `rrset_markdel()`.

## Contract Notes
Callers must unlock returned RRsets. `rrset_cache_touch()` must not be called while holding any RRset lock because it takes locks in the opposite direction from normal slabhash lookup. Reference arrays are expected to be sorted, but duplicate references are explicitly handled.

## Dependencies
Uses packed RRset structures, slabhash/lruhash storage, regional scratch allocation, and config/alloc-cache helpers from Unbound.
