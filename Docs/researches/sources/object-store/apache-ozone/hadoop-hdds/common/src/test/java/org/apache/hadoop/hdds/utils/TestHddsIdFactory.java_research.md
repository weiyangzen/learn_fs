# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/utils/TestHddsIdFactory.java

## Purpose
Tests concurrent uniqueness of IDs produced by `HddsIdFactory`.

## Important APIs, types, and functions
- Uses `HddsIdFactory.getLongId`, `ExecutorService`, `Callable`, `Future`, and a concurrent set.
- Defines cleanup for executor shutdown and helper `addTasks` to submit work.

## Control flow
The test starts multiple tasks that request IDs concurrently, collects them into a concurrent set, waits for all tasks, and asserts no duplicate IDs are produced.

## State and persistence behavior
State is in-memory ID generator state and concurrent collections. No persistence.

## Dependencies and integration points
`HddsIdFactory` supplies unique IDs across HDDS components; concurrency safety is critical for metadata identifiers.

## Risks and test signals
Race conditions in ID generation could cause duplicate metadata IDs. This test signals thread-safety under parallel access.
