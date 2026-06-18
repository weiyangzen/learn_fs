# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/lock/DAGResourceLockTracker.java

Purpose: `DAGResourceLockTracker` enforces lock acquisition constraints for `DAGLeveledResource` values using a dependency DAG. It prevents a thread from acquiring an ancestor-style resource after it already holds dependent child resources.

Important APIs and types: It extends `ResourceLockTracker<DAGLeveledResource>`, is a package-private singleton exposed by `get`, and implements `canLockResource`, `lockResource`, `unlockResource`, and `getCurrentLockedResources`. It maintains an `EnumMap` of per-resource `ThreadLocal<Integer>` hold counts and a precomputed dependency adjacency map.

Control flow: Construction traverses every DAG resource with iterative DFS, building for each resource the transitive set of child resources that block later acquisition. `lockResource` and `unlockResource` update the thread-local count and delegate to the base tracker for details. `canLockResource` returns false if the current thread holds any dependent child resource.

State and persistence behavior: State is process-local, per-thread lock tracking plus static singleton state. No durable state is written.

Dependencies and integration points: It backs OM lock validation for DAG-style resources such as bootstrap and snapshot DB locks.

Risks and test signals: The DFS assumes child adjacency entries are populated before parent computation and the graph is acyclic. Unlocking more times than locking can drive counts negative unless the base tracker guards it. Tests should cover transitive dependency denial, independent lock allowance, reentrant lock counts, singleton thread isolation, and invalid DAG/cycle behavior.
