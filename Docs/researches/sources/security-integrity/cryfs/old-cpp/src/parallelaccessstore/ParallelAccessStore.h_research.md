# sources/security-integrity/cryfs/old-cpp/src/parallelaccessstore/ParallelAccessStore.h

Purpose: keyed resource manager that prevents concurrent duplicate loads, tracks open references, and defers base-store removal until all references to a resource are released.

Important APIs/types/functions: `ParallelAccessStore<Resource, ResourceRef, Key>`, nested `ResourceRefBase`, `OpenResource`, `isOpened`, `add`, `load`, `loadOrAdd`, `remove`, `_resourceToRemoveFuture`, and `release`.

Control flow: `load` locks globally, returns an existing open resource ref or loads from base store and adds it. `ResourceRefBase` destructor calls `release`, decrementing ref count. `remove` registers a promise, destroys or waits for refs to drain, then removes from base store.

State and persistence behavior: `_openResources` owns live resources by key and ref count; `_resourcesToRemove` holds promises for resources pending deletion. Underlying persistence is delegated to `ParallelAccessBaseStore`.

Dependencies and integration points: uses `std::mutex`, `unordered_map`, `boost::promise/future`, `cpputils::unique_ref`, `ASSERT`, and resource refs that must inherit `ResourceRefBase`.

Risks and test signals: file has explicit TODOs about locking, global serialization, race conditions, and missing tests. `remove(const Key&)` reads `_openResources` without taking `_mutex` before `_resourceToRemoveFuture`, which is a concurrency risk.
