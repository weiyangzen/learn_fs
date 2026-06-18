# sources/storage-engines/rocksdb/util/hash_containers.h

Purpose: compile-time abstraction for unordered map/set implementations, allowing folly F14 containers when available and standard containers otherwise.

Important aliases: under `USE_FOLLY`, `UnorderedMap`, `UnorderedMapH`, and `UnorderedSet` alias `folly::F14FastMap/F14FastSet`. Otherwise they alias `std::unordered_map` and `std::unordered_set`.

Control flow: compile-time macro selection only.

State and persistence: no state. Container choice affects in-memory performance and iteration/order characteristics, not persistent format.

Dependencies and integration: includes RocksDB namespace and either folly F14 headers or standard unordered containers. Used by code wanting a centralized hash-container choice.

Risks: folly and std containers differ in performance, memory layout, iterator invalidation details, and possibly iteration order. Code should not depend on container-specific behavior beyond unordered associative semantics.

Test signals: no direct test in this subset.
