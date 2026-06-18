# sources/storage-engines/foundationdb/flow/FastAlloc.cpp

## Purpose
Implements Flow's fixed-size fast allocator, allocator accounting/sampling hooks, keepalive allocation tracking, explicit template instantiations, and a jemalloc alignment regression test.

## Important APIs, Types, And Functions
`FastAllocator<Size>::allocate()`, `release()`, `getMagazine()`, `releaseMagazine()`, `getTotalMemory()`, `getApproximateMemoryUnused()`, and `getActiveThreads()` provide magazine-backed allocation. `ThreadData` keeps per-thread freelists plus an alternate full magazine. `GlobalData` owns global full/partial magazines, totals, and active-thread count under a `CRITICAL_SECTION`. `recordAllocation()` and `recordDeallocation()` provide optional stdout/backtrace sampling. `hugeArenaSample()` records large arena stack traces. `countedNew()`, `countedDelete()`, and `getTotalUnusedAllocatedMemory()` expose accounting. `keepalive_allocator::ActiveScope`, `allocate()`, `invalidate()`, `trackWipedArea()`, and `getWipedAreaSet()` support tests that keep memory alive while tracking invalidated/wiped areas.

## Control Flow
Allocation first diverts to keepalive mode if active, then sanitizer/gperftools/precise-Valgrind paths use aligned system allocation. Normal thread-safe mode pulls from thread-local freelists, swaps in the alternate magazine, or fetches a global/new magazine. Release pushes the object onto the thread freelist and returns an extra full alternate magazine to the global pool. Thread destruction deposits partial and alternate magazines back under the global lock.

## State And Persistence Behavior
State is process-local: thread-local allocator caches, global magazines, counters, instrumentation maps, and trace sampling state. It never persists allocator state, but it may allocate guard-paged blocks and emit TraceEvents/counters.

## Dependencies And Integration Points
Integrates with `FastAlloc.h`, Flow thread primitives, tracing, knobs, random, platform allocation, Valgrind macros, crc32c sampling, jemalloc, ASAN, gperftools, and Arena/packet-buffer users that require 4 KiB alignment for larger size classes.

## Risks And Edge Cases
Correctness depends on strict freelist invariants, per-size alignment, thread-local destructor ordering, and the `INIT_SEG`/`init_priority` setup. Instrumentation deliberately changes allocation paths under Valgrind precise mode and sanitizers. Magazine caches can retain significant unused memory; accounting is approximate because thread-local freelists are excluded. Keepalive mode aborts on mismatched allocate/free tracking.

## Test Signals
The file has a jemalloc-specific `/jemalloc/4k_aligned_usable_size` test. Additional confidence comes from allocator counters, TraceEvents (`GetMagazineSample`, `HugeArenaSample`), sanitizer/Valgrind runs, and broad Flow simulation coverage.
