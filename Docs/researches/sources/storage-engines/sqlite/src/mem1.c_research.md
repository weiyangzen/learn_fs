# sources/storage-engines/sqlite/src/mem1.c

## Purpose

`mem1.c` is SQLite's default low-level allocator for `SQLITE_SYSTEM_MALLOC` builds. It adapts platform memory allocation APIs to the `sqlite3_mem_methods` contract used by `malloc.c`. On most systems it wraps standard `malloc`, `realloc`, and `free`; on supported Apple builds it can use malloc zones; on platforms without a usable allocation-size API it stores the requested size in an 8-byte header preceding each returned allocation.

## Important APIs, Types, And Functions

The allocator methods are `sqlite3MemMalloc`, `sqlite3MemFree`, `sqlite3MemSize`, `sqlite3MemRealloc`, `sqlite3MemRoundup`, `sqlite3MemInit`, and `sqlite3MemShutdown`, installed by the externally visible `sqlite3MemSetDefault()`. Platform macros map to `SQLITE_MALLOC`, `SQLITE_FREE`, `SQLITE_REALLOC`, and optionally `SQLITE_MALLOCSIZE`. The file conditionally uses Apple `malloc_zone_*`, GLIBC-style `malloc_usable_size`, or MSVC `_msize`.

## Control Flow

When no custom allocator, memdebug allocator, Win32 allocator, or fixed heap allocator is selected, `sqlite3MallocInit()` calls `sqlite3MemSetDefault()`, which registers this backend. Allocation calls are guaranteed by the higher layer to have `nByte > 0`. If a platform usable-size function exists, `sqlite3MemMalloc()` directly allocates `nByte` bytes and `sqlite3MemSize()` asks the platform for the usable size. Without such a function, it allocates `nByte + 8`, stores `nByte` in the leading `sqlite3_int64`, and returns the pointer after the header. Freeing and reallocating reverse that header offset. Reallocation similarly relies on the higher layer to pass non-NULL pointers and rounded positive sizes.

`sqlite3MemInit()` performs Apple-specific zone setup. On multi-core systems it uses the default zone; on single-core systems it creates a dedicated SQLite heap zone to reduce global allocator lock contention. Non-Apple initialization is effectively a no-op. Shutdown does not destroy the Apple zone in this code path and otherwise just consumes the unused argument.

## State And Persistence Behavior

The only allocator-local state is the Apple `_sqliteZone_` pointer. Non-Apple system allocator state is owned by the C runtime. If `SQLITE_MALLOCSIZE` is unavailable, each allocation carries an 8-byte persistent header until free/realloc. There is no on-disk persistence. Memory size reporting feeds the higher-level status counters in `malloc.c`, so correctness of `xSize` is essential for soft/hard heap limits and `sqlite3_memory_used()`.

## Dependencies And Integration Points

This file depends on `sqliteInt.h`, the C runtime allocator, optional `<malloc.h>`, Apple `<malloc/malloc.h>` and `<sys/sysctl.h>`, and SQLite logging through `sqlite3_log()` on allocation failure. It plugs into `sqlite3GlobalConfig.m` through `sqlite3_config(SQLITE_CONFIG_MALLOC, ...)`. It is normally used beneath `malloc.c`, which serializes and accounts allocations when memstatus is enabled.

## Risks And Edge Cases

The fallback header mode requires returned pointers to stay 8-byte aligned and requires all frees/reallocs to be passed pointers created by this allocator. Header corruption breaks `xSize` and can cascade into memory accounting failures. Platform usable-size functions may return a usable size larger than requested; higher layers rely on this value for accounting and msize. Apple zone selection is process-global and must be initialized once. Reallocation failure logs the old and new sizes and must leave the original pointer valid. Compile-time detection of `malloc_usable_size` and `_msize` must match headers and runtime ABI.

## Test Signals

Tests should exercise malloc/realloc/free through public SQLite APIs with memstatus on and off, confirm 8-byte alignment, validate `sqlite3_msize()` and memory-used counters, force realloc growth and shrink paths, check OOM logging/fault simulation, and run under platform configurations with and without `SQLITE_MALLOCSIZE`. Apple builds should cover zone initialization paths where feasible.
