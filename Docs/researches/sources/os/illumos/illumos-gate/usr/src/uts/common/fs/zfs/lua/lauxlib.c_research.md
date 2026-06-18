# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lauxlib.c

## Role

`lauxlib.c` implements the Lua auxiliary library, using only the official Lua API. It provides reusable helpers for library authors: tracebacks, argument validation, userdata metatables, buffer building, registry references, loading strings/buffers, module registration, and version checks.

## Main Responsibilities

- Builds compact stack tracebacks with function-name discovery, tail-call notation, and level elision.
- Reports argument errors with method/self adjustment and source-location prefixes.
- Creates, retrieves, validates, and assigns userdata metatables by registry name.
- Implements type and value checkers for strings, numbers, integers, unsigned integers, options, stack space, and arbitrary values.
- Implements `luaL_Buffer` growth and result emission using stack userdata for large temporary buffers.
- Implements the reference free-list system for tables via `luaL_ref` and `luaL_unref`.
- Loads Lua source from memory buffers and strings through `lua_load`.
- Implements metatable lookup/calls, `luaL_len`, `luaL_tolstring`, optional Lua 5.1 module compatibility helpers, `luaL_setfuncs`, `luaL_getsubtable`, `luaL_requiref`, `luaL_gsub`, and `luaL_checkversion_`.

## Integration Points

The file intentionally stays on the public API surface (`lua.h`, `lauxlib.h`) rather than using private core internals. It is therefore a reusable support layer for base, coroutine, bit, and other libraries.

## Risk Notes

Stack balance is the key invariant. Helpers such as `luaL_addvalue`, `luaL_setfuncs`, `luaL_requiref`, traceback generation, and registry references depend on precise stack placement and cleanup. Version checks also validate number-to-integer conversion assumptions for this build.
