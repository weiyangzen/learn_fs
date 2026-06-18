# sources/storage-engines/rocksdb/util/thread_local.cc

## Purpose

Implements `ThreadLocalPtr`, a process-wide registry of per-thread pointer slots keyed by per-instance ids, including cleanup on thread exit and instance destruction.

## APIs, control flow, and state

`StaticMeta` owns the global id allocator, free id list, handler map, mutex, pthread TLS key, and a doubly linked list of all live `ThreadData`. Each thread lazily creates `ThreadData` containing a vector of atomic `Entry` slots and registers it in the global list. `Get`, `Reset`, `Swap`, and `CompareAndSwap` operate on the current thread's vector, resizing under the global mutex when needed. `Scrape` exchanges a replacement across all registered threads and returns non-null old pointers. `Fold` invokes a callback over non-null values under the mutex. `ReclaimId` clears the id from every thread, invokes the registered unref handler, and recycles the id.

## Dependencies and integration

It depends on `port/likely.h`, `util/mutexlock.h`, pthread TLS, and Windows TLS callback machinery where needed. It integrates with RocksDB caches and request-local state that must be scoped by both thread and object instance.

## Risks and test signals

Cleanup handlers run while holding a shared global mutex, so handlers must not reenter `ThreadLocalPtr` APIs. Singleton lifetime is intentionally leaked to avoid destruction-order hazards. Tests cover id recycling, isolated sequential/concurrent access, unref on thread exit and instance destruction, `Swap`, `Scrape`, `Fold`, CAS, and a disabled main-thread-dies-first scenario.
