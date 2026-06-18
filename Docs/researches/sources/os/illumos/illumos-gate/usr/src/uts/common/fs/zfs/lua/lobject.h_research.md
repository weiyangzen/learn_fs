# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lobject.h

## Role

`lobject.h` defines Lua's core runtime object model: tagged values, collectable-object headers, strings, userdata, prototypes, upvalues, closures, tables, nodes, and object access/mutation macros.

## Main Responsibilities

- Defines extra internal tags for prototypes, upvalues, and dead table keys.
- Encodes type variants for Lua closures, light C functions, C closures, short strings, and long strings.
- Defines `TValue`, `Value`, type tests, accessors, false-value logic, collectability tests, liveness checks, and setter macros.
- Supports optional NaN-trick representation.
- Defines `TString`, `Udata`, `Upvaldesc`, `LocVar`, `Proto`, `UpVal`, `CClosure`, `LClosure`, `Closure`, `TKey`, `Node`, and `Table`.
- Defines table sizing helpers, fixed nil object declaration, and object helper declarations.

## Integration Points

This is the central internal header for the Lua runtime. All major subsystems depend on these layouts and macros.

## Risk Notes

The type/tag layout is foundational. Setter macros include liveness checks but not write barriers; callers that store collectable values into already-black objects must invoke the appropriate GC barrier.
