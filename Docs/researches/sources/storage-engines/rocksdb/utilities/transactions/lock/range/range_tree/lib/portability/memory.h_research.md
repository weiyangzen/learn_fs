# sources/storage-engines/rocksdb/utilities/transactions/lock/range/range_tree/lib/portability/memory.h

## Purpose
`memory.h` declares PerconaFT-style allocation wrappers, typed allocation macros, memory status reporting, and hooks for replacing allocator functions in tests.

## Important APIs, Types, And Functions
Functions include startup/shutdown, `toku_malloc`, `toku_calloc`, `toku_xmalloc`, `toku_xcalloc`, aligned variants, realloc variants, `toku_free`, usable-size, dup/string helpers, cleanup/check functions, allocator hook setters, status getter, and footprint helpers. Macros such as `XMALLOC`, `XCALLOC`, `XMALLOC_N`, `XCALLOC_N`, `ZERO_STRUCT`, and `CAST_FROM_VOIDP` make typed allocation concise.

## Control Flow
This header only declares behavior and macros. `x*` functions abort or assert on allocation failure, while plain functions return null and set status in the implementation.

## State And Persistence Behavior
The memory subsystem can keep process-local counters in `memory_status`, including counts, requested/used/freed bytes, max usage, failure sizes, allocator version, and mmap threshold. No DB persistence is involved.

## Dependencies
It includes `<stdlib.h>` and `toku_portability.h` for casts, attributes, and portability macros.

## Integration Points
The locktree code uses `XCALLOC`, `XMALLOC`, `XMALLOC_N`, and `toku_free` for nodes, managers, range buffers, and wait graph nodes. OMT and DBT helpers also rely on this allocation layer.

## Risks And Edge Cases
Allocation macros infer type from the destination variable; misuse is compile-time safer than raw malloc but still manual. Replacing allocator hooks can affect all users globally. Status counters may be approximate under concurrency.

## Test Signals
Memory accounting and leak tests, allocation-failure injection, and range-lock create/destroy stress exercise this layer indirectly.
