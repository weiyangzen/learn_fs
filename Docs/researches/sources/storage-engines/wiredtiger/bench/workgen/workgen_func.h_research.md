# sources/storage-engines/wiredtiger/bench/workgen/workgen_func.h

## Purpose
`workgen_func.h` declares the C bridge functions used by workgen C++ code to access WiredTiger internal utilities safely across the C/C++ boundary.

## Important APIs, Types, and Functions
It forward-declares `struct workgen_random_state` and declares wrappers for 32/64-bit atomics, monotonic clock, epoch time, random allocation/use/free, zero-filled uint64 formatting, and version formatting.

## Control Flow
Consumers include this header under `extern "C"` from C++ internal headers, then call the functions implemented in `workgen_func.c`. The RNG lifecycle is explicit: allocate with a `WT_SESSION`, use, free.

## State and Persistence Behavior
The header defines no state. It exposes an opaque handle so callers cannot depend on `WT_RAND_STATE` layout directly.

## Dependencies and Integration Points
The declarations require WiredTiger types, particularly `WT_SESSION`, to be visible before inclusion. It is included by `workgen_int.h` and implemented by `workgen_func.c`.

## Risks and Edge Cases
Because it is a low-level bridge, signature drift from `workgen_func.c` or missing WiredTiger type declarations will break builds. The opaque random state prevents misuse but also requires strict lifecycle discipline.

## Test Signals
Compile tests covering both C and C++ translation units are the main signal. Link tests should verify every declared wrapper has exactly one implementation.
