# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/lua/lfunc.h

## Role

`lfunc.h` declares closure/prototype/upvalue helpers and closure sizing macros.

## Main Responsibilities

- Defines `sizeCclosure(n)` and `sizeLclosure(n)` for variable-sized closure allocation.
- Declares constructors for prototypes, C closures, Lua closures, and upvalues.
- Declares open-upvalue lookup, upvalue closing/freeing, prototype freeing, and local-name lookup.

## Integration Points

Used by API, call, GC, parser, and VM code whenever closures or prototypes are allocated, freed, or inspected.

## Risk Notes

The closure size macros must match the flexible-array layout in `lobject.h`.
