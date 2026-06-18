# File Research: sources/os/bsd/freebsd-src/sys/sys/counter.h

## Purpose
Declares the kernel scalable 64-bit counter interface and simple rate-check helper API.

## Main Elements
- `counter_u64_t` is a pointer-like opaque counter handle.
- Kernel APIs allocate/free, zero, and fetch counters.
- Array macros allocate, free, copy/fetch, and zero arrays of counters.
- `struct counter_rate` API supports rate checking and retrieving current rate.
- `COUNTER_U64_DEFINE_EARLY()` and sysinit/sysuninit helpers support early counters that become regular per-CPU counters later.

## Dependencies And Integration
In `_KERNEL`, includes `<machine/counter.h>` for MD counter primitives and early counter definitions.

## Risk Notes
Counters are optimized for concurrent updates. Consumers should use fetch/zero interfaces rather than assuming direct scalar storage semantics.
