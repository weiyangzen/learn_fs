# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lgc.h

## Role

`lgc.h` defines the garbage collector state machine, color bits, invariants, barrier macros, and GC API declarations.

## Main Responsibilities

- Defines collector states, sweep-phase tests, generational-mode tests, and invariant predicates.
- Defines object mark bits for white, black, finalized, separated, fixed, and old states.
- Provides bit manipulation helpers and liveness tests.
- Defines `luaC_checkGC`, conditional GC stepping, and value/object write-barrier macros.
- Declares object allocation, barriers, finalizer checks, upvalue color checks, mode changes, steps, full collection, and free-all operations.

## Integration Points

Included by allocation, API, table, string, closure, state, and VM code to preserve collector invariants when object graphs change.

## Risk Notes

Barrier macros depend on correct object/value type tagging. Missing a barrier in callers can create collector-visible corruption that may surface much later.
