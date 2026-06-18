# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/ldebug.h

## Role

`ldebug.h` declares internal debug/error helpers and small macros for program-counter and line mapping.

## Main Responsibilities

- Defines `pcRel`, `getfuncline`, `resethookcount`, and `ci_func`.
- Declares non-returning runtime error helpers for type, concat, arithmetic, ordering, generic run errors, and final error dispatch.

## Integration Points

Included by VM, API, memory, object, and call-path files that need debug metadata or error throwing.

## Risk Notes

`ci_func` assumes an active Lua closure in the `CallInfo`. Callers must only use it in contexts where `isLua(ci)` holds.
