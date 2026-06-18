# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lualib.h

## Purpose

Declares Lua standard library opening functions and standard library names.

## Declared Libraries

- Base
- Coroutine
- Table
- IO
- OS
- String
- Bit32
- Math
- Debug
- Package

## Main API

- `luaL_openlibs(lua_State *L)`: opens all standard libraries.

## Dependencies

- `lua.h`.

## Risks And Notes

- This header declares all standard Lua libraries, but an embedded/kernel build may compile or expose only a subset.
- Defines `lua_assert` as no-op if not already defined.
