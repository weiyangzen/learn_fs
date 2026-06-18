# sources/user-network-fs/mergerfs/vendored/boost/unordered/detail/foa/concurrent_table.hpp

Purpose: Implements the thread-safe fast open-addressing table core used by concurrent flat/node maps and sets.

Important APIs, types, and functions: Key internals include `cache_aligned_array`, `multimutex`, `shared_lock`, `lock_guard`, `scoped_bilock`, `atomic_integral`, `group_access`, `concurrent_table_arrays`, `atomic_size_control`, and `concurrent_table<TypePolicy,Hash,Pred,Allocator>`. Public table operations include visitation, insertion/composite insertion, erasure, merge, clear, assignment, reserve/rehash, stats, equality, and serialization.

Control flow: The table extends `table_core` with atomic group metadata and group-access locks. Container-level access uses a striped `multimutex<rw_spinlock>`; group-level access uses per-group `rw_spinlock`s. Lookups probe by reduced hash, lock only candidate groups, double-check occupancy, then invoke callbacks. Insertions optimistically record the initial group's insertion counter, search for an equivalent key, reserve size and a slot, then roll back and restart if another insertion from the same initial group raced. Rehash and assignment acquire exclusive container access. Serialization takes exclusive access and saves set values or map key/mapped pairs separately; loading clears, reserves, checks duplicates, and throws `bad_archive_exception` on corruption.

State and persistence behavior: Persistent state includes FOA arrays, per-group locks/counters, striped container locks, atomic max-load/size, hash/predicate/allocator state, and optional cumulative stats. Serialization persists elements and version metadata, not lock state.

Dependencies and integration points: Depends on FOA `core.hpp`, reentrancy checks, `rw_spinlock`, tuple rotation helpers, Boost.Serialization hooks, `archive_constructed`, `bad_archive_exception`, and `boost::throw_exception`. Public containers wrap this class.

Risks: Concurrency correctness depends on lock ordering, insertion-counter rollback, atomic metadata, and reentrancy guards. User callbacks must not perform unsupported reentrant table operations. Parallel algorithms depend on standard execution support and still take per-group locks. Archive load rejects duplicates but cannot diagnose all semantic corruption.

Test signals: High-value tests are concurrent insert/find/erase stress, callback mutation, bulk visit, rehash under load, merge with allocator equality, serialization round trips and duplicate archive failures, TSan builds, stats-enabled builds, and exception-safety tests during construction and rehash.
