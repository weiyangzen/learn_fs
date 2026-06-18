# File Research: sources/os/bsd/freebsd-src/sys/sys/atomic_san.h

## Purpose
`atomic_san.h` is a sanitizer interposition layer for FreeBSD `atomic(9)` operations. It is not meant to be included directly; it is pulled through `machine/atomic.h` when a sanitizer runtime supplies `SAN_INTERCEPTOR_PREFIX`.

## Main Interfaces
- Declares sanitizer-prefixed atomic functions for `char`, `short`, `int`, `long`, pointer-sized values, explicit `8/16/32/64` widths, `bool` load/store, and thread/interrupt fences.
- Covers add, clear, compare-and-set, fcmpset, fetchadd, load, acquire-load, read-and-clear, set, subtract, store, release-store, swap, test-and-clear, and test-and-set variants.
- When not compiling `SAN_RUNTIME`, remaps normal `atomic_*` names to sanitizer-prefixed interceptors via macros.

## Implementation Notes
The file is almost entirely macro-generated declarations and macro aliases. Pointer load/store receive special casts so typed pointer users retain usable types while the interceptor operates on `uintptr_t`. This header is central for kernel sanitizers because it lets atomic accesses be observed without changing callers.

## Dependencies and Constraints
Requires `_MACHINE_ATOMIC_H_`, `sys/types.h`, `SAN_INTERCEPTOR_PREFIX`, and `__CONCAT`. The aliases are intentionally disabled inside sanitizer runtime code to avoid recursively intercepting the sanitizer's own implementation.
