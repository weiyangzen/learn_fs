# sources/storage-engines/rocksdb/util/cleanable.cc

Purpose: implements `Cleanable` cleanup callback chains and `SharedCleanablePtr`, a reference-counted wrapper around a `Cleanable` used to share cleanup ownership among objects and transfer cleanup responsibilities.

Important APIs and functions: `Cleanable` initializes an embedded head cleanup node, runs `DoCleanup` in its destructor, supports move construction/assignment by transferring the head/list, and disables source cleanup after move. `DelegateCleanupsTo` registers each cleanup with another `Cleanable`, preserving ownership by transferring heap nodes where possible. `RegisterCleanup(Cleanup*)` installs a heap node or fills the embedded head. `RegisterCleanup(CleanupFunction, void*, void*)` either fills the embedded head or allocates a new cleanup node. `SharedCleanablePtr::Impl` extends `Cleanable` with relaxed atomic ref counting. `SharedCleanablePtr` supports allocate/reset/copy/move/destruction, dereference, registering a copy with a target cleanable, and moving its reference as a cleanup to a target.

Control flow and state: `Cleanable` stores one cleanup inline to avoid allocation for the common single-callback case and a linked list for extras. `SharedCleanablePtr` starts `Impl::ref_count` at one, increments on copies or registered virtual copies, and deletes the impl on the final `Unref`, triggering `Cleanable` cleanup.

Dependencies and integration: includes `rocksdb/cleanable.h`, atomics, assertions, and utility moves. Integration search shows cache handles, DB iterator/read paths, and shared cleanup pinning using `Cleanable` and `SharedCleanablePtr`.

Risks and test signals: move assignment asserts no self-move and would be unsafe if violated in release builds. `DelegateCleanupsTo` can reorder callbacks because `RegisterCleanup` inserts heap nodes near the head. Ref counting uses relaxed atomics, which is adequate only if object lifetime is otherwise synchronized around cleanup data. No direct test in this subset; behavior is heavily exercised indirectly by cache and iterator pinning tests.
