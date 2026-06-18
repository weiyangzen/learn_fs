# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ltablib.c

## Purpose

Implements Lua’s standard `table` library.

## Library Functions

Registers:

- `table.concat`
- `table.insert`
- `table.pack`
- `table.unpack`
- `table.remove`
- `table.sort`
- optional `table.maxn` under `LUA_COMPAT_MAXN`
- optional global `unpack` under `LUA_COMPAT_UNPACK`

## Core Behavior

- `insert` appends or shifts entries upward to insert at a validated position.
- `remove` returns the removed entry, shifts entries down, and nils the old tail.
- `concat` concatenates table elements in a requested range with an optional separator.
- `pack` creates an array-like table and stores argument count in field `n`.
- `unpack` pushes a range of raw integer-indexed table entries with stack overflow checks.
- `sort` uses quicksort with median-of-three pivoting, tail-recursion reduction, and optional comparator function.

## Dependencies

- Public Lua API and auxiliary checks: `lua.h`, `lauxlib.h`.
- Standard library declarations: `lualib.h`.

## Risks And Notes

- `sort` detects invalid order functions when partition scans cross bounds.
- Length comes from `luaL_len`, so sparse-table behavior follows Lua length semantics.
- Integer positions use `int`, so very large table lengths can be constrained by C integer limits.
