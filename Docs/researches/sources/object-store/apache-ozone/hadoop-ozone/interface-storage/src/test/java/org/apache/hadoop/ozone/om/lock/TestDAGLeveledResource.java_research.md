# sources/object-store/apache-ozone/hadoop-ozone/interface-storage/src/test/java/org/apache/hadoop/ozone/om/lock/TestDAGLeveledResource.java

Purpose: Unit test ensuring `DAGLeveledResource` remains acyclic.

Important APIs/types/functions: `ensureNoCycleInDAGLevelResource()` constructs a Guava directed graph containing every enum value and edges from each resource to its children, then asserts `Graphs.hasCycle(graph)` is false.

Control flow, state, and persistence: Test-only control flow. It models lock-order dependencies and checks graph validity; no runtime state is persisted.

Dependencies and integration points: Uses Guava graph utilities and JUnit. It protects the lock-ordering contract used by hierarchical OM resource locks.

Risks: The test only checks cycles, not semantic correctness of the order. A wrong but acyclic edge set could still allow unsafe lock behavior.

Test signals: Direct regression signal for accidental cycles in resource ordering.
