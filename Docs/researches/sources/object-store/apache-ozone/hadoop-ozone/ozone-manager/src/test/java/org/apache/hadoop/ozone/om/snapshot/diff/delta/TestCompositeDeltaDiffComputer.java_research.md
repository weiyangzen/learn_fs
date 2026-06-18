# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/TestCompositeDeltaDiffComputer.java

## Purpose
`TestCompositeDeltaDiffComputer` validates the orchestration layer that chooses between RocksDB checkpoint DAG diffing and full SST comparison for OM snapshot diff delta-file discovery. It isolates `CompositeDeltaDiffComputer` with Mockito construction mocking so the tests can assert constructor choices, fallback rules, status reporting, close behavior, and non-native diff augmentation without invoking real RocksDB diff machinery.

## Important APIs, Types, and Functions
- `CompositeDeltaDiffComputer` is the system under test; it is constructed with `OmSnapshotManager`, active `OMMetadataManager`, a delta directory, a `Consumer<SubStatus>`, `fullDiff`, and `nonNativeDiff`.
- `RDBDifferComputer` is mocked as the preferred DAG-walk implementation when `fullDiff` is false.
- `FullDiffComputer` is mocked as the always-available fallback and as the direct implementation when `fullDiff` is true.
- `computeDeltaFiles(SnapshotInfo, SnapshotInfo, Set<String>, TablePrefixInfo)` returns `Optional<Map<Path, Pair<Path, SstFileInfo>>>`, where keys are source SST paths and values contain the linked delta path plus SST metadata.
- `SubStatus.SST_FILE_DELTA_DAG_WALK` and `SubStatus.SST_FILE_DELTA_FULL_DIFF` are asserted as progress signals.
- The non-native diff path uses `FullDiffComputer.getSSTFileSetForSnapshot`, `OmSnapshotManager.getActiveSnapshot`, `RDBStore.getDbLocation`, and inode checks via `IOUtils.getINode`.

## Control Flow
The constructor tests verify that `RDBDifferComputer` is built only in normal mode, while `FullDiffComputer` is built in both normal and full-diff-only modes. Success cases force the RDB differ mock to return maps with one, many, or zero SST files and confirm no fallback call occurs. Fallback cases force `Optional.empty()` or a runtime exception from the RDB differ and assert that full diff is invoked and its result is returned. Full-diff-only mode skips RDB construction entirely and reports only the full-diff status.

The non-native diff test first returns one RDB-differ SST and then mocks the from-snapshot database to expose two SSTs. With `nonNativeDiff=true`, the final result contains the RDB output plus from-snapshot files linked into the delta directory. With `nonNativeDiff=false`, only RDB output is returned.

## State and Persistence Behavior
The tests use `@TempDir` for delta and mock DB paths, creating concrete SST files to validate hard links. State is transient and cleaned by `close()`. Non-native mode has the most persistence relevance: it creates linked delta files for from-snapshot SSTs and asserts those links share inodes with the source files, which protects delete detection behavior when native RocksDB diffing is disabled.

## Dependencies and Integration Points
The file integrates with snapshot metadata (`SnapshotInfo`), OM snapshot lookup (`OmSnapshotManager` and `UncheckedAutoCloseableSupplier<OmSnapshot>`), RocksDB store metadata (`RDBStore`), table prefix filtering (`TablePrefixInfo`), and `SstFileInfo`. Mockito `mockConstruction` and `mockStatic` are critical to decouple the composite from concrete diff implementations and static SST scanning.

## Risks and Edge Cases
Important risks covered include accidentally constructing or invoking RDB diff in full-diff mode, treating an empty successful RDB result as a failure, missing status updates, failing to close child computers, and losing delete coverage in non-native mode by omitting from-snapshot SST files. A residual risk is that constructor argument propagation to child diff computers is mostly inferred from construction count rather than captured argument inspection.

## Test Signals
The test suite is a strong behavioral signal for fallback semantics, status sequencing, and link-based non-native diff output. It does not run real RocksDB checkpoint traversal; those semantics are delegated to companion tests for `RDBDifferComputer` and `FullDiffComputer`.
