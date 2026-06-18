# sources/storage-engines/rocksdb/memory/memory_usage.h

Purpose: Template helpers for approximate memory usage of hash-map containers.

Important APIs/types/functions: `ApproximateMemoryUsage(std::unordered_map<...>)` and optional `ApproximateMemoryUsage(folly::F14FastMap<...>)`.

Control flow and state: unordered-map estimate adds object size, per-entry value plus next pointer, and bucket array size. Folly implementation delegates to `getAllocatedMemorySize` plus object size.

State and persistence behavior: pure calculation over container state; no mutation or persistence.

Dependencies and integration points: RocksDB memory accounting code for in-memory metadata maps; optional Folly support.

Risks: estimates are approximate and allocator/container-implementation dependent. The unordered-map formula may drift with STL implementation details.

Test signals: no direct tests in this subset; correctness is approximate by design.
