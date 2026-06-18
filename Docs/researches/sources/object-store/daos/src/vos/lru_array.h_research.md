# sources/object-store/daos/src/vos/lru_array.h

## Purpose
Declares and partially implements the generic LRU array abstraction. The header contains public types, flags, index helpers, lookup/peek/allocation inline APIs, and internal circular-list helpers used by the C file.

## Important APIs, Types, And Functions
`struct lru_callbacks` defines lifecycle hooks. `struct lru_entry`, `struct lru_sub`, and `struct lru_array` define the cache layout. Flags are `LRU_FLAG_EVICT_MANUAL` and `LRU_FLAG_REUSE_UNIQUE`; `LRU_NO_IDX` marks empty lists. Public macros include `lrua_lookupx`, `lrua_lookup`, `lrua_peekx`, `lrua_peek`, `lrua_allocx`, `lrua_alloc`, and `lrua_allocx_inplace`; C-file APIs allocate, free, evict, and aggregate arrays.

## Control Flow
Header lookups compute subarray and entry index via bit masks, validate key match, optionally promote to MRU, and return typed payloads. Allocation macros call `lrua_find_free`; in-place allocation allocates the subarray if absent, verifies the target slot is free, removes it from the free list, inserts it in the active list, and returns the payload.

## State And Persistence
All state is volatile. Payload memory is colocated after the `lru_entry` table in each subarray allocation. Circular lists use entry indexes, not pointers, so entries remain stable within a subarray.

## Dependencies And Integration
Depends on `daos/common.h` list and assertion utilities. Designed for VOS caches that need stable integer handles and callback-driven cleanup.

## Risks
The inline-heavy API means misuse can compile but corrupt list state if callers pass stale indexes or wrong keys. `lrua_alloc` uses the address of the index variable as a default key, so persistent indexes must be logged before mutation as documented. Manual mode requires explicit eviction by the owner.

## Test Signals
Header behavior should be tested via typed callers: lookup vs peek MRU effects, allocation key matching, in-place duplicate rejection, and subarray index/mask conversions.
