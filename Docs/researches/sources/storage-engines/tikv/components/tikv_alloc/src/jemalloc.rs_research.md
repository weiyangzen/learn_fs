# sources/storage-engines/tikv/components/tikv_alloc/src/jemalloc.rs

## Purpose
This file is the full jemalloc-backed implementation of `tikv_alloc`. It installs `tikv_jemallocator::Jemalloc`, exposes allocator stats, supports optional heap profiling, tracks per-thread allocation counters, and optionally maps threads to exclusive jemalloc arenas.

## Important APIs, Types, and Control Flow
`Allocator` aliases `tikv_jemallocator::Jemalloc`. Global maps track thread memory accessors and thread-to-arena mappings. `PeekableRemoteStat<T>` wraps raw jemalloc thread-local statistic pointers and reads them atomically; `MemoryStatsAccessor` records allocated/deallocated pointers plus thread name. `add_thread_memory_accessor` registers the current thread, and `remove_thread_memory_accessor` removes both memory and arena state.

`dump_stats` calls `malloc_stats_print`, then appends per-thread allocation data. `fetch_stats` advances the jemalloc epoch and returns allocated, active, metadata, resident, mapped, retained, dirty, and fragmentation values. `iterate_thread_allocation_stats` trims thread-pool numeric suffixes and aggregates by logical thread name. `iterate_arena_allocation_stats` deduplicates `(thread_name, arena)` pairs before reading resident, mapped, and retained arena stats.

With `mem-profiling`, the nested `profiling` module controls `prof.active`, `prof.dump`, `prof.reset`, background threads, arena creation, `thread.arena`, and profiling sample rate. Without that feature, profiling APIs return disabled errors or no-op values.

## State, Dependencies, and Integration
State is process-global behind mutexes and jemalloc mallctl state. Safety depends on registered threads calling `remove_thread_memory_accessor` before exit because remote TLS pointers can otherwise dangle. Integration points include `tikv_jemalloc_ctl`, `tikv_jemalloc_sys`, thread wrappers, metrics collectors, and profiling tools.

## Risks and Test Signals
Key risks are unsafe remote TLS reads, stale map entries, feature/runtime mismatch for profiling, unwraps in stats paths, and arena accounting skew if thread names or arena reuse are unexpected. Tests cover non-empty stats dumps, approximate allocation/deallocation counters, arena-map cleanup, deduplication for same arena, and ignored profiling dump/activation cases gated by `MALLOC_CONF`.
