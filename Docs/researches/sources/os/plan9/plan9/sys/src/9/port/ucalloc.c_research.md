# File Research: sources/os/plan9/plan9/sys/src/9/port/ucalloc.c

## Role

Provides an uncached-memory allocator backed by the Plan 9 pool allocator. It is intended for DMA or hardware paths that require cache-inhibited memory.

## Main Data

`ucpool` is a `Pool` named `"Uncached"` with 4 MiB max size, 1 MiB arenas, and 32-byte quantum. A private lock/message buffer serializes pool diagnostics and panic printing.

## Control Flow

`ucarena` allocates a 1 MiB aligned cached arena, maps it uncached with `mmuuncache`, and temporarily increases `mainmem->maxsize` while doing so. `ucallocalign` allocates from `ucpool`, asserts the request fits within an arena, and zeroes successful allocations. `ucalloc` uses 32-byte alignment. `ucfree` returns memory to the pool.

## Dependencies

Depends on `<pool.h>`, `mallocalign`, `mmuuncache`, `mainmem`, `msize`, kernel locks, and Plan 9 panic/print routines.

## Risks

The allocator assumes 1 MiB arena allocation and successful uncached remapping semantics. `ucallocalign` asserts on large requests rather than returning an error. The panic path copies diagnostic text out before unlocking, which is correct but tightly coupled to the pool callback contract.
