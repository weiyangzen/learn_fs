# File Research: sources/os/bsd/freebsd-src/sys/sys/dnv.h

## Purpose
Declares default-returning nvlist lookup and take helpers.

## Main Elements
- `dnvlist_get_*` returns a typed value or caller-provided default when the named value is absent or of another type.
- `dnvlist_take_*` removes and returns the typed value or returns caller-provided default.
- Supported types include bool, number, string, nvlist, descriptor, and binary.

## Dependencies And Integration
Uses `sys/_nv.h`; outside kernel it includes standard types and `sys/nv_namespace.h`.

## Risk Notes
Pointer defaults and returned pointers have different ownership semantics depending on get versus take. Callers must not free internal get results.
