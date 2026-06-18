# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/TestFullDiffComputer.java

## Purpose
`TestFullDiffComputer` validates full SST-file diffing between two OM snapshots. It ensures that full diff identifies SST files that may contain changes for selected tables and bucket prefixes, and that returned files are hard-linked through the common file-link delta mechanism.

## Important APIs, Types, and Functions
- `FullDiffComputer.computeDeltaFiles` compares live SST metadata from source and target snapshots.
- `FullDiffComputer.getDeltaFiles` goes through the public base API and verifies inode identity for linked outputs.
- `SstFileInfo` carries file name, key range, and column family.
- `TablePrefixInfo` filters diff candidates by table-to-prefix mapping.
- The helper `createMockSnapshot` builds mocked `OmSnapshot`, `OMMetadataManager`, `RDBStore`, `RocksDatabase`, `ManagedRocksDB`, and `RocksDB` chains and creates real hard links at snapshot DB paths.

## Control Flow
A parameterized method supplies multiple source/target SST metadata maps, table prefix maps, expected diff files, and lookup table sets. For each case, temporary source SST files are created, mock snapshots expose corresponding RocksDB live metadata, and `computeDeltaFiles` is invoked. The expected result is normalized to snapshot directory paths and compared against actual `SstFileInfo` values. The public `getDeltaFiles` path is then called to ensure delta links point to the same inodes as the selected source files.

## State and Persistence Behavior
The test creates real filesystem directories and hard links under `@TempDir`. Snapshot DB locations are represented by `snapDirectory/snapshotName`, and SST file paths are linked to shared underlying files. `close()` is expected to delete the delta directory. No durable OM metadata is written; persistence is simulated through RocksDB metadata and file paths.

## Dependencies and Integration Points
The test integrates with RocksDB live-file metadata (`LiveFileMetaData`), HDDS Rocks DB wrappers, snapshot handles, active snapshot lookup, and OM table-prefix filtering. It models the behavior needed by snapshot diff report generation when checkpoint differ traversal is unavailable or disabled.

## Risks and Edge Cases
The cases cover equal sets, source-only and target-only files, invalid key prefixes, multiple tables, and lookup-table filtering. Key risks are false positives from unrelated tables, false negatives when a file range crosses a bucket prefix, and incorrect link paths. The mock RocksDB layer means compaction timing and real RocksDB metadata quirks are not exercised.

## Test Signals
This is the main test signal for full-diff correctness. It verifies both logical diff selection and physical link identity, which together protect the downstream merge/report stage from missing required SST data.
