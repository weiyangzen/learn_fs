# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltm.c

## Purpose

Implements tag-method/metamethod name initialization and lookup helpers.

## Main APIs

- `luaT_init`: interns and fixes all metamethod names.
- `luaT_gettm`: optimized table metamethod lookup used by `fasttm`; caches absence for fast-access metamethods.
- `luaT_gettmbyobj`: retrieves the relevant metatable for tables, userdata, or primitive types and returns the event value.

## Core Behavior

- Defines human-readable type names in `luaT_typenames_`.
- Interns `__index`, `__newindex`, `__gc`, `__mode`, `__len`, `__eq`, arithmetic/comparison names, `__concat`, and `__call`.
- Caches absent fast metamethods by setting bits in `Table.flags`.

## Dependencies

- `lobject.h`, `lstate.h`, `lstring.h`, `ltable.h`, `ltm.h`.

## Risks And Notes

- The order of `luaT_eventname` must match the `TMS` enum in `ltm.h`.
- `luaT_gettm` asserts `event <= TM_EQ`; later metamethods are not absence-cached through this path.
