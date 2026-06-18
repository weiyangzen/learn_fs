# File Research: sources/os/bsd/freebsd-src/sys/sys/bus_san.h

## Purpose
`bus_san.h` is the sanitizer interposition layer for `bus_space(9)` memory-mapped I/O accessors.

## Main Interfaces
- Declares sanitizer-prefixed bus-space functions for read/write, multi, region, stream, set, copy, peek, poke, and mapping helpers.
- Supports widths 1, 2, 4, and 8 using `uint8_t`, `uint16_t`, `uint32_t`, and `uint64_t`.
- When not compiling `SAN_RUNTIME`, remaps normal `bus_space_*` names to sanitizer-prefixed interceptors.

## Implementation Notes
The header mirrors `atomic_san.h` for bus-space operations. It lets kernel sanitizers observe device memory accesses without changing each bus driver. The miscellaneous mapping helpers include map, unmap, subregion, alloc, free, and barrier.

## Dependencies and Constraints
Requires inclusion through `machine/bus.h` and a `SAN_INTERCEPTOR_PREFIX`. Runtime code disables aliases to avoid intercepting its own interceptor implementations.
