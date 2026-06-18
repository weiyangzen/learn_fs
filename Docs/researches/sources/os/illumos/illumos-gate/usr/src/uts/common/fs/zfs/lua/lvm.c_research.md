# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lvm.c

## Purpose

Implements the Lua virtual machine execution engine and core runtime operations for arithmetic, comparison, table access, concatenation, length, closures, hooks, and bytecode dispatch.

## Main APIs

- `luaV_execute`: main bytecode interpreter loop.
- `luaV_finishOp`: completes an opcode interrupted by yield.
- `luaV_gettable`, `luaV_settable`: table indexing/assignment with metamethod handling.
- `luaV_arith`: arithmetic with numeric conversion and metamethod fallback.
- `luaV_concat`: concatenation with conversion and `__concat`.
- `luaV_objlen`: length operation with `__len`.
- `luaV_lessthan`, `luaV_lessequal`, `luaV_equalobj_`: comparison/equality semantics.
- `luaV_tonumber`, `luaV_tostring`: conversion helpers.

## Core Behavior

- Dispatches all Lua 5.2 VM opcodes including loads, upvalues, table ops, arithmetic, comparisons, tests, calls, tail calls, returns, numeric/generic loops, `SETLIST`, closures, varargs, and `EXTRAARG`.
- Handles metamethod loops with a `MAXTAGLOOP` bound.
- Performs hook dispatch for line/count hooks and preserves yield semantics from hooks/metamethods.
- Reuses cached closures when a prototype’s upvalue identities match.
- Maintains stack and `CallInfo` invariants across calls, tail calls, returns, GC checks, and stack reallocations.

## illumos/ZFS Adaptations

- Defines `strcoll(l,r)` as `strcmp((l),(r))`.
- Patches division and modulo behavior using Lua 5.3.2-derived `luaV_div` and `luaV_mod` to avoid divide-by-zero crashes under integral `lua_Number`.
- `OP_DIV` and `OP_MOD` use patched helpers directly in the fast numeric path.

## Dependencies

- Call/stack/error support: `ldo.h`, `ldebug.h`.
- Functions/upvalues: `lfunc.h`.
- GC barriers: `lgc.h`.
- Objects/opcodes/state/strings/tables/metamethods: `lobject.h`, `lopcodes.h`, `lstate.h`, `lstring.h`, `ltable.h`, `ltm.h`.

## Risks And Notes

- Integral `lua_Number` changes division, modulo, comparison, formatting, and binary chunk behavior relative to stock double-based Lua.
- Yield-resume paths in `luaV_finishOp` must match every opcode that can yield through a metamethod or call.
- `luaV_gettable`/`luaV_settable` protect against metamethod cycles via `MAXTAGLOOP`.
- Stack pointers can be invalidated by calls and GC; the VM uses `Protect` and recomputes `base`/`ra`.
