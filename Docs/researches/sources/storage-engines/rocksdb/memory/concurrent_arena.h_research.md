# sources/storage-engines/rocksdb/memory/concurrent_arena.h

Purpose: Thread-safe allocator wrapper around `Arena` using fast arena locking and lazily used per-core shards for small allocations.

Important APIs/types/functions: `ConcurrentArena`, `Allocate`, `AllocateAligned`, `ApproximateMemoryUsage`, `MemoryAllocatedBytes`, `AllocatedAndUnused`, `IrregularBlockNum`, `AllocateImpl`, `Shard`, `Fixup`, `ShardAllocatedAndUnused`.

Control flow and state: large allocations, forced huge-page aligned allocations, and early uncontended allocations go directly to the arena under `arena_mutex_`. Otherwise a shard is selected via TLS/core-local state; if the shard lacks space, it reloads from the main arena with a shard block sized to minimize waste. Aligned requests are rounded to pointer alignment before sharding.

State and persistence behavior: allocations share arena lifetime. Atomic counters mirror arena accounting plus shard unused space.

Dependencies and integration points: used in concurrent memtable allocation paths where many writer threads allocate small nodes.

Risks: accounting is approximate under relaxed atomics. Fragmentation can occur in per-core shards. `AllocateAligned` uses `(bytes - 1)` and therefore assumes `bytes > 0`.

Test signals: not directly tested here; behavior is covered through broader memtable/concurrency tests elsewhere.
