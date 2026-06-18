# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/filter/AbstractReclaimableFilterTest.java

## Purpose
`AbstractReclaimableFilterTest` is a shared fixture for reclaimable snapshot garbage-collection filter tests. It builds mocked Ozone Manager, snapshot chain, bucket metadata, locks, snapshot cache, and RocksDB surfaces so concrete tests can focus on reclaimability decisions for keys, directories, and rename entries.

## Important APIs, Types, and Functions
- `initializeFilter(...)` is the abstract factory implemented by subclasses.
- `setup(...)` creates mock OM state, snapshot chain state, bucket layout, and the concrete `ReclaimableFilter`.
- `mockSnapshotChain` creates `SnapshotInfo` lists per volume/bucket and stubs `SnapshotUtils.getSnapshotInfo`, `getPreviousSnapshot`, and `getLatestSnapshotInfo`.
- `mockOmSnapshotManager` constructs a real `OmSnapshotManager` while mocking `ManagedRocksDB.open`, `SnapshotDiffManager`, `SnapshotCache`, `OmSnapshotLocalDataManager`, transaction table state, and RocksDB iterators.
- Accessors expose `reclaimableFilter`, `snapshotInfos`, `snapshotChainManager`, `omSnapshotManager`, `keyManager`, lock IDs, volumes, and buckets.

## Control Flow
`setup` constructs the mock OM, chain manager, key manager, and a lock that records acquired snapshot IDs and asserts release symmetry. It builds a configurable grid of volumes and buckets, creates a snapshot chain for each bucket, stubs bucket lookup and volume IDs, then initializes and spies the concrete filter. The selected `currentSnapshotInfo` may be null to represent the active object store rather than a specific snapshot.

## State and Persistence Behavior
The fixture creates a temporary metadata directory and mocks transaction info as flushed through `TransactionInfo.valueOf(0, 10)`. Snapshot status and last transaction info can be modified via a supplied `Function<SnapshotInfo, SnapshotInfo>` to test inactive or unflushed snapshots. The lock ID `AtomicReference` is the key state assertion for GC lock correctness.

## Dependencies and Integration Points
The fixture ties together `OzoneManager`, `OmMetadataManagerImpl`, `OmSnapshotManager`, `SnapshotChainManager`, `SnapshotUtils`, `SnapshotCache`, `SnapshotDiffManager`, `OmSnapshotLocalDataManager`, RocksDB wrappers, bucket manager, key manager, and `IOzoneManagerLock`. It is tightly coupled to snapshot GC internals.

## Risks and Edge Cases
The helper's heavy mocking can hide integration drift, especially constructor changes in `OmSnapshotManager` or metadata manager behavior. It does, however, guard important edge cases: inactive snapshots, unflushed transaction info, nonexistent volumes/buckets, and lock release ID mismatches.

## Test Signals
This fixture is the backbone for all reclaimable filter tests. Its strongest signal is consistent setup of snapshot-chain windows and GC read-lock acquisition for the snapshots consulted by a filter.
