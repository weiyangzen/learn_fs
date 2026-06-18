# sources/user-network-fs/nfs-ganesha/src/include/netgroup_cache.h

## Purpose

`netgroup_cache.h` declares a small cache wrapper around `innetgr()` for export/client access decisions based on netgroups.

## Important APIs, Types, and Functions

The API is `ng_cache_init`, `ng_clear_cache`, and `ng_innetgr(group, host)`. `ng_innetgr` returns whether a host is a member of a netgroup and is expected to cache both lookup results and possibly misses.

## Control Flow

Export/client authorization code initializes the cache, calls `ng_innetgr` during client matching, and clears cached results after configuration or directory-service changes.

## State and Persistence Behavior

State is process-local cache contents derived from system name-service lookups. There is no durable persistence; correctness depends on explicit clear/reinit or TTL behavior in the implementation.

## Dependencies and Integration Points

The header is intentionally minimal. It integrates with export access lists, libc/NSS netgroup support, and configuration reload paths.

## Risks and Test Signals

Risks include stale netgroup membership, host canonicalization mismatches, NSS latency hidden by cache, and missing `<stdbool.h>` if included in isolation. Tests should cover hit/miss caching, cache clearing, host aliases/FQDNs, negative results, NSS failure recovery, and concurrent lookups during reload.
