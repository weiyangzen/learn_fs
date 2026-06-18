# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestSimpleStriped.java

## Purpose
Tests `SimpleStriped` read/write lock behavior against Guava-style striped locks.

## Important APIs, types, and functions
- Uses `SimpleStriped`, Guava `Striped`, `ReadWriteLock`, and `ReentrantReadWriteLock`.
- Test case is `testReadWriteLocks`.

## Control flow
The test creates striped read/write locks, retrieves locks for keys, and asserts lock identity/behavior matches expected striping semantics.

## State and persistence behavior
State is in-memory lock arrays/stripes. No persistence.

## Dependencies and integration points
Striped locks are used to reduce lock cardinality while protecting keyed resources in HDDS.

## Risks and test signals
Incorrect striping can map keys inconsistently or allocate wrong lock types. This test signals basic lock factory behavior.
