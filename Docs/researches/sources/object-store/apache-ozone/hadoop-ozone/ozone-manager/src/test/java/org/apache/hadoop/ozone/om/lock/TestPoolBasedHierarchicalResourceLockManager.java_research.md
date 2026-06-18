# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/lock/TestPoolBasedHierarchicalResourceLockManager.java

Purpose: tests `PoolBasedHierarchicalResourceLockManager`, the pool-backed hierarchical lock implementation for DAG resources, covering basic locking, resource-wide locks, key-level locks, pool limits, cleanup semantics, and DAG order enforcement.

Important APIs/types: `PoolBasedHierarchicalResourceLockManager`, `HierarchicalResourceLockManager.HierarchicalResourceLock`, `DAGLeveledResource`, `IOzoneManagerLock.Resource`, and configuration keys `OZONE_OM_HIERARCHICAL_RESOURCE_LOCKS_SOFT_LIMIT` / `HARD_LIMIT`.

Control flow: setup creates a fresh manager and teardown closes it. Basic tests acquire read/write locks with try-with-resources. Concurrency tests use `CompletableFuture`, latches, and fixed thread pools to confirm write exclusivity, resource-wide exclusion against keyed read/write locks, and read/write interactions. Stress tests run many keys across threads. Custom limit tests fill the pool to the hard limit, confirm a new acquisition blocks, then release one lock to allow progress. The DAG order test iterates all DAG resource pairs and enforces forbidden ordering for snapshot content and bootstrap locks.

State and persistence behavior: no persistent state; the manager maintains an in-memory pool of resource-key lock objects and an acquired flag on handles. Pool soft/hard limits are stateful capacity controls.

Dependencies and integration points: integrates with the same snapshot DAG resource model used by OM locks. Tests rely on Java concurrency primitives, Ozone configuration, and JUnit timeouts.

Risks: several assertions depend on scheduling and sleeps. The test name typo `testResouce...` is harmless but visible. It catches normal IOException propagation only superficially.

Test signals: validates close idempotence, null validation, empty and varied key strings, reentrant read behavior, concurrent stress, pool blocking, and DAG lock-order failures.
