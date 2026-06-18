# sources/storage-engines/foundationdb/fdbserver/resolver/ConflictSet.cpp

Purpose: implements the resolver conflict detection engine used to decide which transactions in a commit batch can commit. It records write conflict history by key range/version and checks incoming read ranges against that history plus intra-batch writes.

Important APIs and functions: `newConflictSet`, `clearConflictSet`, and `destroyConflictSet` manage opaque state. `ConflictBatch::addTransaction` converts commit transactions into sorted read/write boundary points and read conflict descriptors. `detectConflicts` sorts points, checks historical read conflicts, checks intra-batch conflicts with `MiniConflictSet`, combines non-conflicting write ranges, merges them into the skip list, and removes old history. The internal `SkipList` stores boundary keys with max versions per level; `ReadConflictRange`, `KeyInfo`, and `sortPoints` optimize batch processing.

Control flow, state, and persistence: state is in-memory `ConflictSet` with a version-history skip list, oldest version, and removal cursor key. No durable persistence exists; recovery rebuilds resolver state elsewhere. Bug injection can ignore too-old/read/write sets in simulation.

Dependencies and integration: consumes `CommitTransactionRef`, Flow arenas, `ConflictBatchStatus`, `ResolverBug`, key ranges, and unit-test macros. `Resolver.cpp` creates a `ConflictBatch` per resolve request.

Risks and test signals: risks are boundary ordering semantics, skip-list max-version maintenance, memory allocator correctness, conflicting-key reporting, and old-version pruning. Tests include `skipListTest` and `miniConflictSetCompatibility`; additional signals are accepted/conflicted/too-old resolver counters and deterministic simulation failures.
