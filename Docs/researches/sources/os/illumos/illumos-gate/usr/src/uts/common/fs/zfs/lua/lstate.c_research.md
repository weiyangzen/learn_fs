# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstate.c

## Purpose

Implements creation, initialization, thread allocation, and teardown of Lua runtime state for the embedded ZFS Lua interpreter.

## Main APIs

- `lua_newstate(lua_Alloc f, void *ud)`: allocates main `lua_State` plus `global_State`, seeds hashing, initializes GC state, and runs protected runtime initialization.
- `lua_close(lua_State *L)`: closes the main thread and frees all runtime state.
- `lua_newthread(lua_State *L)`: creates a coroutine/thread sharing the same global state.
- `luaE_freethread(lua_State *L, lua_State *L1)`: frees a thread.
- `luaE_extendCI`, `luaE_freeCI`: manage dynamic call-info frames.
- `luaE_setdebt`: adjusts GC accounting while preserving total allocation accounting.

## Core Behavior

- `stack_init` allocates the initial Lua stack and base `CallInfo`.
- `init_registry` creates the registry and stores `LUA_RIDX_MAINTHREAD` and `LUA_RIDX_GLOBALS`.
- `f_luaopen` initializes stack, registry, string table, tag-method names, lexer reserved words, memory-error string, and runtime version.
- `makeseed` mixes `gethrtime()`, stack/heap/global/function addresses, and `luaS_hash` to seed string/table hashing.
- `close_state` closes upvalues, frees all GC objects, string table, global buffer, stack, and the top-level allocation.

## Dependencies

- Memory and protected-call internals: `lmem.h`, `ldo.h`.
- GC and object lifecycle: `lgc.h`, `lfunc.h`, `lstring.h`, `ltable.h`.
- Lexer/metamethod initialization: `llex.h`, `ltm.h`.

## Risks And Notes

- Partial initialization failures are handled through `luaD_rawrunprotected`; `close_state` must tolerate partially built state.
- `lua_close` always closes the main thread, even if called with a coroutine.
- Hash seed generation is adapted for illumos via `gethrtime()`.
