# File Research: sources/os/bsd/netbsd-src/sys/sys/null.h

## Purpose
Defines `NULL` portably for C, C++, and older/newer GNU C++ cases.

## Main API
- `NULL` as `((void *)0)` for C.
- `NULL` as `0` for C++ except newer GNU C++ where `__null` is used.

## Dependencies
None.

## Risks and Notes
This is a small compatibility header. It only defines `NULL` when it is not already defined.
