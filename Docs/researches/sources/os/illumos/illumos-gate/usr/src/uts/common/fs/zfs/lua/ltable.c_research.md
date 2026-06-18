# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltable.c

## Purpose

Implements Lua table storage: split array/hash layout, lookup, insertion, resizing, iteration, and length-boundary search.

## Main APIs

- `luaH_new`, `luaH_free`
- `luaH_get`, `luaH_getint`, `luaH_getstr`
- `luaH_set`, `luaH_setint`, `luaH_newkey`
- `luaH_resize`, `luaH_resizearray`
- `luaH_next`
- `luaH_getn`

## Core Behavior

- Tables have an array part for positive integer keys and a hash part for all other keys.
- Array size is chosen so at least half the slots up to the chosen power-of-two boundary are used.
- Hash part uses chained scatter with Brent’s variation; if a colliding node is not in its main position, insertion moves it to preserve lookup performance.
- Short-string lookups use interned-string pointer/hash fast path.
- Long-string keys lazily compute their hash in `mainposition`.
- `luaH_next` traverses array entries first, then hash nodes.
- `luaH_getn` implements Lua length boundary search using binary search in array part or exponential/binary search into hash part.

## Dependencies

- Lua object model and equality: `lobject.h`, `lvm.h`.
- Memory/GC/error support: `lmem.h`, `lgc.h`, `ldebug.h`, `ldo.h`.
- State and strings: `lstate.h`, `lstring.h`.

## Risks And Notes

- `luaH_newkey` rejects nil and NaN table keys.
- Callers of `luaH_set` must handle write barriers and metamethod-cache invalidation as needed.
- `lastfree` scanning and dummy-node handling are important for empty hash tables.
- Length behavior follows Lua’s boundary semantics and is undefined for sparse arrays with multiple valid boundaries.
