# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/atomic.h

## Purpose

`atomic.h` declares illumos atomic operations and memory-barrier primitives.

## Atomic Operations

The header provides typed increment, decrement, add, OR, AND, compare-and-swap, and swap functions for 8/16/32-bit integers, `uchar_t`, `ushort_t`, `uint_t`, `ulong_t`, pointers, and 64-bit values where available. Most operations have both no-return and `_nv` variants, with comments warning that `_nv` can be more expensive and should be used only when the new value is needed atomically.

Exclusive bit set/clear helpers operate on `ulong_t` bit positions and report whether the bit was already in the requested state.

## Memory Barriers

`membar_enter`, `membar_exit`, `membar_producer`, and `membar_consumer` define lock acquisition/release and producer/consumer ordering semantics.

## Research Notes

This is a foundational concurrency ABI used throughout kernel code. Filesystem and storage code rely on these routines for refcounts, lock-free flags, queue state, and memory ordering.
