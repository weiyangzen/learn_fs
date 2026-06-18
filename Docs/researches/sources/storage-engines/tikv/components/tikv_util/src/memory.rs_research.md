# sources/storage-engines/tikv/components/tikv_util/src/memory.rs

## Purpose
Provides low-level memory accounting helpers for TiKV utility code: approximate heap-size estimation for common container/protobuf types, unsafe vector layout conversion, and an atomic quota counter that can reject or force account allocations. It is performance-sensitive and favors O(1) approximations over deep traversal.

## Important APIs, Types, and Functions
- `unsafe fn vec_transmute<F, T>(Vec<F>) -> Vec<T>` reinterprets a vector after debug-checking size and alignment; correctness depends entirely on the caller preserving layout invariants.
- `trait HeapSize` exposes `approximate_heap_size` and `approximate_mem_size`; implementations exist for scalars, `Vec<T>`, `Option<T>`, tuples, `HashMap<K,V>`, `Either`, and selected `kvproto` structures.
- `MemoryQuotaExceeded` is the lightweight error for denied quota allocations.
- `MemoryQuota` owns `in_use: AtomicIsize` and `capacity: AtomicUsize`, with `new`, `in_use`, `used_ratio`, `capacity`, `set_capacity`, `alloc`, `alloc_force`, and `free`.
- `OwnedAllocated` is an RAII allocation token that records bytes successfully allocated from an `Arc<MemoryQuota>` and returns them on drop.

## Control Flow
`HeapSize` implementations compute capacity-based estimates; `Vec<T>` and `HashMap<K,V>` sample the first element/key-value pair to avoid O(n) deep scans. `MemoryQuota::alloc` first checks the current capacity and hard maximum, then atomically increments `in_use`; if a concurrent race pushes usage beyond capacity, it rolls the addition back and returns `MemoryQuotaExceeded`. `free` subtracts bytes and compensates if over-freeing would drive the counter negative. `alloc_force` bypasses capacity but still respects `MAX_MEMORY_ALLOC_SIZE`.

## State and Persistence Behavior
All quota state is in process memory through atomics. No durable persistence exists. `OwnedAllocated` couples state lifetime to Rust drop semantics, so leaking or forgetting the owner leaks quota accounting until process exit. Capacity can be changed dynamically with relaxed atomic stores.

## Dependencies and Integration Points
The file depends on `kvproto` protobuf structs for size estimates, `collections::HashMap`, crate-level `Either`, logging macros, and atomics. It is suitable for cache admission, request accounting, and components that need coarse memory pressure checks without allocator introspection.

## Risks
`vec_transmute` is unsafe and can cause undefined behavior if element layouts diverge. Heap-size estimates are approximate and can undercount shared protobuf bytes or heterogeneous collections. `used_ratio` divides by capacity and assumes capacity is not zero in callers. Relaxed atomics are adequate for approximate accounting but should not be treated as strict synchronization.

## Test Signals
Unit tests cover single-thread and multi-thread quota accounting, resize behavior, RAII release, force allocation, hard maximum behavior, and representative heap-size estimates for vectors, tuples, options, and hash maps.
