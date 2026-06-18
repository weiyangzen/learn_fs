# sources/distributed-fs/xrootd/src/XrdSys/XrdSysRAtomic.hh

Purpose: defines `XrdSys::RAtomic`, a relaxed-memory-order atomic wrapper for integral, pointer, and boolean types, plus typedef aliases matching common scalar names.

Important APIs/types/functions: the primary template supports relaxed assignment, conversion, increment/decrement, arithmetic/bitwise compound operations, fetch bit operations, compare-exchange, exchange, and `load()`. The pointer specialization supports pointer arithmetic and `operator->()`. The bool specialization supports assignment, conversion, compare-exchange, exchange, and `load()`.

Control flow: most operators directly call the matching `std::atomic` method with `std::memory_order_relaxed`, returning either the old value for post operations or the computed new value for pre/compound operations. Compare-exchange and exchange allow callers to override memory order.

State and persistence: each wrapper owns one `std::atomic<T>` member. No locking or persistence exists beyond the object's lifetime.

Dependencies and integration: includes `<atomic>`, `<cstddef>`, and `<cstdint>`. XrdThrottle uses it for advisory counters, relaxed wake-order arrays, and per-user EWMA/accounting values where strict ordering is not required.

Risks: relaxed ordering is intentional but dangerous if callers use these atomics for multi-variable synchronization without an external lock. The pointer compare-exchange signatures use `T&` for the expected argument instead of `T*&`, which is suspicious for pointer atomics. Return types for compare-exchange are declared as `T`/`T*` but `std::atomic::compare_exchange_*` returns `bool`; this works only through implicit conversion for scalar specializations and is semantically misleading.

Test signals: compile use cases for all typedefs, pointer arithmetic, volatile overloads, and compare-exchange call sites; add concurrency tests only for atomicity, not ordering guarantees.
