<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestCoderUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestCoderUtil.java

## Purpose
`TestCoderUtil` validates concurrency behavior of the shared zero-buffer cache in `CoderUtil`.

## Important APIs, Types, and Functions
It resets the private static `emptyChunk` via reflection in `resetEmptyChunk`, tests `getEmptyChunkDoesNotShrinkWhenCacheGrowsConcurrently`, and uses helper `waitUntilBlocked`.

## Control Flow
The test creates two tasks: one requesting a slightly larger chunk and blocking on class initialization/locking, and another requesting a larger chunk. It verifies the final cache remains at the larger length and the smaller request receives a sufficiently large array.

## State and Persistence Behavior
It deliberately mutates static `CoderUtil.emptyChunk` between tests.

## Dependencies and Integration Points
It depends on reflection, executor services, futures, atomic references, AssertJ, and JUnit.

## Risks and Test Signals
Risks include brittle thread-block detection and reflective access breaking on field rename. Passing tests signal the double-check locking in `getEmptyChunk` avoids cache shrink races.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestCoderUtil.java -->
