# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltable.h

## Purpose

Declares Lua table operations and node-access macros.

## Key Definitions

- `gnode`, `gkey`, `gval`, `gnext`: access table hash nodes.
- `invalidateTMcache`: clears cached absence flags for metamethod lookup.
- `keyfromval`: derives a node key pointer from its value pointer.

## APIs

- Lookup/set/allocation/resizing/freeing APIs implemented in `ltable.c`.
- Debug-only `luaH_mainposition` and `luaH_isdummy`.

## Risks And Notes

- `keyfromval` relies on `Node` field layout and is pointer-arithmetic-sensitive.
- `invalidateTMcache` must be called when table mutations can affect metamethod lookup assumptions.
