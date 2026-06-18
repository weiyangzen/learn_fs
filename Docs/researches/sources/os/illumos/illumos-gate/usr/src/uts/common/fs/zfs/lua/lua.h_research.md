# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lua.h

## Purpose

Public Lua 5.2.4 C API header, adapted to include ZFS kernel context and local `luaconf.h`.

## Main Contents

- Version constants: Lua 5.2 release 5.2.4.
- Basic public types: `lua_State`, `lua_CFunction`, `lua_Reader`, `lua_Writer`, `lua_Alloc`, `lua_Number`, `lua_Integer`, `lua_Unsigned`.
- Type tags and status/error codes.
- Registry pseudo-index and registry predefined keys.
- Public state, stack, access, push, get, set, load/call, coroutine, GC, and miscellaneous APIs.
- Convenience macros for common stack/API operations.
- Debug API event codes, masks, `lua_Hook`, and `lua_Debug`.

## Dependencies

- Includes `<sys/zfs_context.h>` and `luaconf.h`.

## Risks And Notes

- This header exposes the ABI expected by the embedded Lua runtime; `luaconf.h` changes such as `lua_Number=int64_t` affect chunk compatibility and API behavior.
- `lua_dump` here has the Lua 5.2 three-argument public signature, while internal dump helpers may carry strip flags.
- Debug metadata structure layout is part of the public API for debug hooks.
