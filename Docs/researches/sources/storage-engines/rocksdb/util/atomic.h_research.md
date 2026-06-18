# sources/storage-engines/rocksdb/util/atomic.h

Purpose: wraps `std::atomic` so RocksDB call sites make memory ordering explicit and avoid accidental sequential consistency or invalid memory-order combinations. It also centralizes deprecated pre-C++20 atomic `shared_ptr` free-function usage behind compiler warning suppression.

Important APIs and types: `RelaxedAtomic<T>` exposes only relaxed operations: `StoreRelaxed`, `LoadRelaxed`, weak/strong CAS, exchange, and fetch arithmetic/bitwise operations. `Atomic<T>` derives from it and adds acquire/release/acq_rel versions: release stores, acquire loads, acq_rel CAS/exchange/fetch operations. `AtomicSharedPtrLoad` and `AtomicSharedPtrStore` call `std::atomic_load_explicit` and `std::atomic_store_explicit` with pragma guards for Clang and GCC deprecation warnings.

Control flow and state: wrappers are thin inline calls around an internal `std::atomic<T> v_`. They do not add persistence, logging, or locking. The type distinction forces callers to choose relaxed-only vs acquire-release capable state.

Dependencies and integration: depends on `<atomic>`, `<memory>`, and namespace headers. It is a shared utility for performance-sensitive concurrent code, and conceptually pairs with `bit_fields.h` for packed atomic state.

Risks and test signals: the wrappers deliberately omit seq_cst variants; callers with rare seq_cst requirements must not misuse acquire-release operations. `RelaxedAtomic` is only correct when not synchronizing other data. `compare_exchange_*` uses a single memory order, so failure ordering follows standard rules for that overload. There is no dedicated test in the subset; confidence comes from simple mapping to standard atomics and compile-time use across the codebase.
