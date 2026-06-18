# sources/storage-engines/sqlite/src/mem2.c

## Purpose

`mem2.c` implements SQLite's debug low-level allocator for `SQLITE_MEMDEBUG` builds. It wraps each allocation with guard words, optional title text, optional backtrace storage, allocation type metadata, linked-list tracking of outstanding allocations, randomized fill patterns, and allocation-size statistics. Its purpose is to expose leaks, buffer overruns, use-after-free, incorrect allocation type use, and stale pointer assumptions during development and tests.

## Important APIs, Types, And Functions

The key metadata type is `struct MemBlockHdr`, which records requested size, doubly linked list pointers, backtrace counts, title size, allocation type (`MEMTYPE_HEAP`, `MEMTYPE_LOOKASIDE`, or related masks), and a foreguard. A rear guard word follows the rounded allocation. Static methods include `adjustStats`, `sqlite3MemsysGetHeader`, `sqlite3MemSize`, `sqlite3MemInit`, `sqlite3MemShutdown`, `sqlite3MemRoundup`, `randomFill`, `sqlite3MemMalloc`, `sqlite3MemFree`, and `sqlite3MemRealloc`. Externally visible debug helpers include `sqlite3MemSetDefault`, `sqlite3MemdebugSetType`, `sqlite3MemdebugHasType`, `sqlite3MemdebugNoType`, `sqlite3MemdebugBacktrace`, `sqlite3MemdebugBacktraceCallback`, `sqlite3MemdebugSettitle`, `sqlite3MemdebugSync`, `sqlite3MemdebugDump`, and `sqlite3MemdebugMallocCount`.

Global allocator state is grouped in `mem`: mutex, outstanding allocation list head/tail, backtrace depth and callback, title buffer, allocation-disallow counter, and per-size allocation/current/highwater arrays.

## Control Flow

Allocation enters `sqlite3MemMalloc()`, takes the debug allocator mutex, asserts allocations are currently allowed, rounds the request to 8 bytes, computes total bytes for title, backtrace slots, header, payload, and rear guard, then calls system `malloc`. On success it links the header onto the outstanding list, stores guard words and metadata, captures a GLIBC backtrace if enabled, copies title text, updates size-class statistics, fills the user payload with pseudo-random data, fills rounded padding bytes with `0x65`, and returns the payload pointer.

Freeing calls `sqlite3MemsysGetHeader()` first, which validates foreguard, rear guard, and padding bytes. It then unlinks the header from the outstanding list, updates statistics, overwrites the entire allocation record with pseudo-random bytes, and calls system `free`. Reallocation always allocates a new block, copies the overlap, random-fills any growth, and frees the old block. This deliberately makes stale uses of the old pointer more likely to fail.

Debug type APIs only inspect or mutate headers when the active allocator's `xFree` is this module's `sqlite3MemFree`; otherwise they return permissive results so asserts remain valid with other allocators. Dump APIs walk outstanding allocations and optionally print captured backtraces and size-class counts.

## State And Persistence Behavior

There is no disk persistence. In-process state persists until shutdown or process exit: outstanding allocations remain on a linked list for leak reporting, size-class counters accumulate allocation attempts and current/highwater usage, title text applies to subsequent allocations, and backtrace settings affect future allocations. Each allocation stores its own metadata and guard words for lifetime validation.

## Dependencies And Integration Points

This file depends on `sqliteInt.h`, system `malloc/free`, `<stdio.h>`, optional GLIBC `backtrace` APIs, SQLite mutexes, and SQLite memory debug type constants. It integrates beneath `malloc.c` as the selected `sqlite3_mem_methods` backend. Higher-level code uses `sqlite3MemdebugSetType/HasType/NoType` in assertions to distinguish heap and lookaside ownership.

## Risks And Edge Cases

Because this allocator asserts on corruption, it is intended for testing, not graceful production recovery. Incorrect mutex assumptions can occur when `sqlite3GlobalConfig.bMemstat` means the higher wrapper already holds the static memory mutex; `sqlite3MemInit()` accounts for that by only allocating its own mutex when needed. Backtrace depth is capped and rounded, so callers should not assume arbitrary depth. Padding checks only catch writes into rounded slack or guard words, not all intra-buffer logic errors. `sqlite3MemdebugSync()` assumes a backtrace callback is installed. Realloc always moving memory can expose stale pointers but also changes performance and fragmentation characteristics compared with production allocators.

## Test Signals

Test signals include intentional guard corruption assertions, leak dump output containing outstanding allocations and titles, backtrace callback invocation, malloc count growth, allocation type assertions for heap/lookaside transitions in `malloc.c`, randomized fill exposing uninitialized reads, freed-memory fill exposing use-after-free, and realloc movement exposing stale old-pointer use. Debug test suites should run with `SQLITE_MEMDEBUG` and both memstatus modes.
