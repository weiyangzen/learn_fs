# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/stddef.h

## Role

Provides common `<stddef.h>`-style support for `offsetof`.

## Key Contents

Defines `offsetof(s, m)` if not already defined. Uses `__builtin_offsetof` for GCC 4.1 and newer. Falls back to address-of-null-member expressions, casting to `std::size_t` in C++98-or-newer or `size_t` in C.

## Design Notes

This is a compact compatibility header with no type definitions beyond the macro.
