# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/impl/TestContainerSet.java

## Purpose
`TestContainerSet` is a JUnit 5 test suite for `ContainerSet`, the in-memory datanode registry of container IDs to `Container<?>` instances. It verifies core map semantics, report/list APIs, per-volume indexes, on-demand scan delegation, and the write-lock acquisition protocol used when concurrent disk-balancer-style remapping may swap a container instance.

## Important APIs, Types, And Functions
- `ContainerSet.addContainer`, `getContainer`, `removeContainer`, `containerCount`, `listContainer`, `getContainerReport`, `getContainerMapIterator`, and iterable support are exercised with `KeyValueContainer` and `KeyValueContainerData`.
- `getContainerIterator(HddsVolume)` and `containerCount(HddsVolume)` are tested through mocked `HddsVolume` instances that maintain a `ConcurrentSkipListSet<Long>` of container IDs via `addContainer` and `removeContainer`.
- `registerOnDemandScanner`, `scanContainer`, and `scanContainerWithoutGap` integrate with `OnDemandContainerScanner`.
- `getContainerWithWriteLock` is tested via Mockito spies to simulate stable mappings, removed mappings, remapped containers, and retry exhaustion.
- `ContainerLayoutTestInfo.ContainerTest` runs most tests over supported `ContainerLayoutVersion` variants.

## Control Flow
The tests build containers with deterministic IDs and alternating open/closed states. Basic map tests add a container, assert duplicate insert raises `StorageContainerException`, retrieve by ID, and remove it. Iterator tests traverse both the `ContainerSet` iterable and map iterator and validate state by ID parity. Listing tests request a window from a start ID and assert returned IDs are ascending. Volume tests attach `KeyValueContainerData` to mocked volumes and assert per-volume iterators/counts reflect additions and removals. Scan tests first call scan methods without a scanner, then register a mocked scanner and verify only existing containers trigger scanner callbacks. Write-lock tests drive `getContainerWithWriteLock` through repeated `getContainer` responses to prove it locks the candidate, rechecks map identity after lock acquisition, unlocks stale candidates, retries swaps, and returns `null` after `maxContainerMapSwapRetries()`.

## State And Persistence Behavior
The suite focuses on in-memory state rather than disk persistence. `ContainerSet` is expected to maintain a main ID map and secondary volume indexes. `KeyValueContainerData` carries persisted-style metadata such as state, volume reference, max size, layout, and last data scan time; the tests use these fields to verify ordering and reporting but do not create container directories. Last-scan ordering requires never-scanned containers to sort before scanned containers, then by scan time and container ID tie-break.

## Dependencies And Integration Points
The file depends on Ozone container types (`KeyValueContainer`, `KeyValueContainerData`, `ContainerData`), HDDS protobufs (`ContainerReportsProto`, `ContainerProtos`), mocked `HddsVolume`, and `OnDemandContainerScanner`. `ContainerImplTestUtils.newContainerSet()` is the local test factory. Integration points under test include datanode container reporting, scanner scheduling, and volume-aware container lookup.

## Risks And Edge Cases
Important risk coverage includes duplicate container insertion, missing container lookup/removal, scanner calls for non-existent IDs, stale per-volume indexes after removal, scan-time ordering instability, and write-lock leaks when a container is removed or swapped during acquisition. The write-lock tests are especially concurrency-sensitive: they assert the caller receives a locked live object and stale locks are released.

## Test Signals
Strong behavioral signals are present for map semantics, iterator ordering, report count, list pagination, per-volume counts, scanner dispatch, and lock retry correctness. The tests use mocks heavily and do not exercise real disk persistence or multi-threaded races, but the simulated swap sequences encode the expected concurrency contract.
