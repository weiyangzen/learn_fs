## sources/storage-engines/foundationdb/bindings/flow/HighContentionAllocator.h

Purpose: declares the allocator used by `DirectoryLayer` to assign unique directory prefixes under contention.

Important APIs and types: constructor accepts a parent `Subspace` and derives `counters` as child 0 and `recent` as child 1. Public `allocate` returns a future string prefix; static `windowSize` exposes the range sizing policy.

Control flow: callers hold a transaction and await `allocate`; implementation performs all reads/writes inside that transaction so allocation participates in commit conflict checking.

State and persistence: allocator state is stored under the supplied subspace. The header itself only stores the two child subspaces.

Dependencies and integration points: includes `Subspace.h`; used by `DirectoryLayer` as `allocator(rootNode.get(HIGH_CONTENTION_KEY))`.

Risks: API is small, but callers must not treat allocation as durable until the surrounding transaction commits.

Test signals: directory creation tests cover this through automatic prefix assignment.
