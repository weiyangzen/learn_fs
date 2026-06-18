# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lauxlib.h

## Role

`lauxlib.h` declares the Lua auxiliary-library API and convenience macros used to build Lua C libraries.

## Main Responsibilities

- Defines `luaL_Reg`, `LUA_ERRFILE`, and pre-defined reference constants.
- Declares argument checking, metatable, traceback, buffer, reference, load, length, string substitution, registration, and module helper functions.
- Provides macros for common type checks, optional arguments, loading strings/buffers, opening libraries, and generic buffer append operations.
- Defines `luaL_Buffer`, including the fixed initial buffer and stack-backed expansion protocol.

## Integration Points

This is the public support header for Lua libraries in this embedded runtime. Library files include it to register functions and validate Lua arguments.

## Risk Notes

The macros wrap stack-mutating operations. Callers must account for their stack effects, especially `luaL_newlib`, `luaL_getmetatable`, `luaL_opt`, and buffer macros.
