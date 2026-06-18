# File Research: sources/os/bsd/freebsd-src/sys/sys/stdarg.h

## Purpose
`stdarg.h` is a minimal wrapper exposing FreeBSD's internal standard-argument definitions.

## Main Interfaces
- Includes `sys/_stdarg.h`.

## Implementation Notes
No types or macros are defined directly here; the header only provides the public include guard and delegates.

## Dependencies and Constraints
Depends entirely on `sys/_stdarg.h`.
