# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_MemoryLeak.cpp

Purpose: verifies `QueueMap` correctly constructs and destroys key/value objects despite custom memory management.

Important APIs/types/functions: `QueueMapTest_MemoryLeak`, `EXPECT_NUM_INSTANCES`, `MinimalKeyType::instances`, `MinimalValueType::instances`, `push`, `pop`, and keyed `pop`.

Control flow: executes push/pop sequences and compares live instance counters after each scenario.

State and persistence behavior: queue-map in-memory entries own key/value instances; counters reflect live object state.

Dependencies and integration points: inherits `QueueMapTest` fixture and uses minimal test key/value types.

Risks and test signals: strong leak/double-destruction signal for common pop paths. It does not cover replacement of an existing key unless helper behavior includes it elsewhere.
