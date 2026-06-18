# sources/storage-engines/rocksdb/util/core_local.h

Purpose: provides `CoreLocalArray<T>`, a small utility for sharding frequently accessed state by physical CPU core to reduce contention and false sharing.

Important APIs and types: `CoreLocalArray<T>::Size()` reports the allocated shard count. `Access()` returns the element for the current core. `AccessElementAndIndex()` returns both pointer and index so callers can remember where an object came from. `AccessAtCore(size_t)` returns a specific shard and asserts bounds.

Control flow: construction reads `std::thread::hardware_concurrency()`, then chooses a power-of-two shard count at least eight. `AccessElementAndIndex()` calls `port::PhysicalCoreID()`. If the core id is unavailable, it chooses a random shard from the thread-local random generator. Otherwise it maps the core id with `BottomNBits(cpuid, size_shift_)`, which is a fast modulo for power-of-two sizes.

State and persistence: owns a `std::unique_ptr<T[]>` for process-local state only. The template does not enforce cache alignment, but comments tell users to make `T` cache aligned when false sharing matters.

Dependencies and integration points: depends on port core-id support, `Random::GetTLSInstance()`, and `BottomNBits()`. Used by compression context caching, statistics, concurrent arena sharding, and memtable range tombstone caches.

Risks: hardware concurrency can return zero on some platforms; because the minimum shift starts at 3, the array still has eight entries. Physical core ids can exceed the shard count and are folded by low bits, which can collide on some topology layouts. Cached indices can be inaccurate after thread migration, so callers should only cache them when documented tolerance exists.

Test signals: exercised indirectly by users such as compression context cache and statistics. There is no local direct test for CPU-id fallback distribution or alignment assumptions.
