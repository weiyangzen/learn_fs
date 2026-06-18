# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/main/java/org/apache/hadoop/ozone/om/lock/DAGLeveledResource.java

Purpose: Enum of hierarchical lock resources that define DAG-based lock ordering for OM snapshot/bootstrap-related resources.

Important APIs/types/functions: Values are `SNAPSHOT_GC_LOCK`, `SNAPSHOT_DB_LOCK`, `SNAPSHOT_LOCAL_DATA_LOCK`, `SNAPSHOT_DB_CONTENT_LOCK`, and `BOOTSTRAP_LOCK`. Each implements `IOzoneManagerLock.Resource` via `getName()` and `getResourceManager()`, and exposes `getChildren()` for lock ordering.

Control flow, state, and persistence: Each enum constant owns a `ResourceManager` holding thread-local lock timing. Child sets represent allowed downstream lock acquisition order: `SNAPSHOT_DB_CONTENT_LOCK` precedes DB/local-data locks, and `BOOTSTRAP_LOCK` precedes all snapshot locks. This is runtime concurrency state only, not persisted metadata.

Dependencies and integration points: Used by hierarchical lock manager implementations and snapshot/bootstrap code to avoid deadlocks. Integrates with `IOzoneManagerLock.ResourceManager`.

Risks: Introducing a cycle or incorrect parent/child edge can create deadlocks or block valid lock sequences. The constructor filters self-dependencies but does not detect larger cycles at runtime.

Test signals: `TestDAGLeveledResource.ensureNoCycleInDAGLevelResource` builds a Guava directed graph from enum values/children and asserts it has no cycle.
