# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lstate.h

## Purpose

Defines Lua global state, per-thread state, call-frame state, GC object union, and core state-management declarations.

## Key Structures

- `stringtable`: interned short-string hash table.
- `CallInfo`: stack frame metadata for Lua and C calls, including saved PC/base for Lua functions and continuation/error metadata for C calls.
- `global_State`: allocator, GC accounting/lists, string table, registry, hash seed, global buffer, panic handler, main thread, fixed memory-error string, tag-method names, and per-type metatables.
- `lua_State`: per-thread execution stack, current call info, hook state, open upvalues, error jump, and base C-call frame.
- `GCObject`: union over all collectable object types: strings, userdata, closures, tables, prototypes, upvalues, and threads.

## Important Constants

- `EXTRA_STACK`: extra stack slots for metamethod calls and runtime internals.
- `BASIC_STACK_SIZE`: initial stack size.
- `KGC_NORMAL`, `KGC_EMERGENCY`, `KGC_GEN`: GC modes.
- `CIST_*`: call-status flags for Lua/C frame state, yields, protected calls, tail calls, and hooks.

## Public/Internal APIs

- `luaE_setdebt`
- `luaE_freethread`
- `luaE_extendCI`
- `luaE_freeCI`

## Risks And Notes

- GC list comments describe object ownership invariants; violating these breaks collector reachability.
- `CallInfo` state is central to VM reentry/yield behavior.
- `gettotalbytes(g)` combines `totalbytes + GCdebt`; allocation accounting assumes that invariant.
