# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lcorolib.c

## Role

`lcorolib.c` implements Lua's coroutine library.

## Main Responsibilities

- Creates coroutine threads with `coroutine.create`.
- Resumes coroutines with argument/result transfer across Lua states sharing the same global state.
- Implements `wrap`, which converts resume failures into raised Lua errors with location information.
- Implements `yield`, `status`, and `running`.
- Registers the coroutine library through `luaopen_coroutine`.

## Integration Points

The library is a public wrapper around core thread APIs: `lua_newthread`, `lua_resume`, `lua_yield`, `lua_xmove`, `lua_status`, and stack inspection.

## Risk Notes

The code carefully handles dead coroutine detection, too many arguments/results, and stack transfer failures. Coroutine behavior is constrained by `ldo.c` yieldability rules.
