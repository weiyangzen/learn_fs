# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/TestRDBDifferComputer.java

## Purpose
`TestRDBDifferComputer` validates the delta-file computer that delegates snapshot diff discovery to `RocksDBCheckpointDiffer`. It checks constructor behavior, snapshot-local-data conversion to differ inputs, version mapping, hard-link creation, resource closure, and error propagation.

## Important APIs, Types, and Functions
- `RDBDifferComputer` is constructed from `OmSnapshotManager`, active `OMMetadataManager`, delta path, and activity reporter.
- `RocksDBCheckpointDiffer.getSSTDiffListWithFullPath` is the core integration point; it receives `DifferSnapshotInfo` objects, a version map, `TablePrefixInfo`, and lookup tables.
- `OmSnapshotLocalDataManager.ReadableOmSnapshotLocalDataProvider` supplies current and previous `OmSnapshotLocalData`.
- `OmSnapshotLocalData.VersionMeta` and `getVersionSstFileInfos` drive version ancestry mapping for the differ.

## Control Flow
The constructor tests assert that the active store and checkpoint differ are obtained, but a null differ still allows object construction. Success tests configure snapshot local data, mock differ output, invoke `computeDeltaFiles`, and confirm every returned source SST is linked into the delta directory. Empty differ output and null differ both return `Optional.empty()`. Version mapping tests capture the map passed to the differ and assert the expected mapping from current versions to previous versions. Error tests cover missing version metadata and `IOException` from the differ.

## State and Persistence Behavior
The test uses real temporary SST files and verifies hard-link inode equality. Snapshot-local-data providers are explicitly verified as closed, including when the differ throws. The metadata manager's persistent delegation is mocked; the state under test is local-data version metadata and transient delta links.

## Dependencies and Integration Points
This file connects OM snapshot-local metadata, RocksDB checkpoint differ, table prefix filtering, and file-link output. It is the unit boundary between Ozone snapshot management and the lower-level `org.apache.ozone.rocksdiff` package.

## Risks and Edge Cases
Covered risks include absent checkpoint differ, empty differ result, multiple table output, corrupt or empty version metadata, propagated I/O failure, unclosed local data providers, and repeated synchronized differ calls. The synchronization test calls sequentially rather than with real threads, so race protection is inferred from repeated safe invocations.

## Test Signals
The tests are strong indicators for correct differ wiring and cleanup. They do not prove RocksDB differ algorithm correctness, but they verify Ozone's adapter supplies the right metadata and handles failures in the expected fallback-friendly form.
