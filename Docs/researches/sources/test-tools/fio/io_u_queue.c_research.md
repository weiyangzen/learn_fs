# sources/test-tools/fio/io_u_queue.c

## Purpose
Implements allocation and cleanup for fio's simple `io_u` pointer stack queue and circular requeue ring.

## Important APIs, Types, and Functions
Defines `io_u_qinit`, `io_u_qexit`, `io_u_rinit`, and `io_u_rexit`. Inline push/pop operations live in `io_u_queue.h`.

## Control Flow
`io_u_qinit()` allocates a pointer array with `smalloc()` for shared allocations or `calloc()` for local allocations, then initializes count and max. `io_u_rinit()` rounds `nr + 1` up to a power of two, allocates the ring array, and initializes head/tail. Exit functions free the corresponding allocation.

## State and Persistence Behavior
State is in-memory queue arrays plus counters. There is no persistence.

## Dependencies and Integration Points
Depends on `io_u_queue.h` and `smalloc`. Used by thread-data initialization for freelists and requeue rings consumed by `io_u.c`.

## Risks
Ring capacity uses one empty slot to distinguish full from empty and requires power-of-two masking. The power-of-two rounding only shifts through 16 bits, so very large queue sizes would need review on 64-bit values. Exit functions do not null pointers or reset counts.

## Test Signals
Unit tests should cover shared and non-shared allocation, exact power-of-two and non-power-of-two ring sizes, push/pop ordering, full assertions in debug builds, and cleanup under sanitizers.
