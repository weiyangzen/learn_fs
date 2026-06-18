# sources/storage-engines/foundationdb/fdbrpc/ReplicationPolicy.cpp

`ReplicationPolicy.cpp` implements replica-selection policy composition over locality sets.

`IReplicationPolicy` provides convenience selection/validation, `validateFull()`, and locality tracing helpers. `PolicyOne` selects or validates one available entry. `PolicyAcross` enforces a child policy across distinct values of a locality attribute. `PolicyAnd` composes multiple policies in sorted order. Test helpers serialize and deserialize policies.

Control flow in `validateFull()` checks solved and unsolved outcomes and verifies selected solutions are minimal by removing entries. `PolicyAcross::selectReplicas()` first considers already-selected `alsoServers`, caches locality key lookup for simple across-one patterns, records candidate additions, chooses lower-added candidates first, then randomly scans remaining mutable entries by unused locality value. It rolls back appended results if the count cannot be satisfied. `PolicyAnd::selectReplicas()` threads a growing result vector through child policies and appends only new selections.

State includes configured policy counts/attributes/children plus temporary member vectors and arenas used during selection. There is no disk persistence, but policies serialize through Flow binary serialization. Dependencies include `ReplicationPolicy.h`, `Replication.h`, `LocalitySet`, deterministic random, TraceEvents, and `g_replicationdebug`.

Risks are policy-correctness bugs in rollback, minimality validation, group-key mapping, cache assumptions, random mutable-entry swapping, and new locality attributes. `/ReplicationPolicy/Serialization` tests round-trip simple and nested policies by comparing `info()`, but does not exhaustively prove selection behavior.
