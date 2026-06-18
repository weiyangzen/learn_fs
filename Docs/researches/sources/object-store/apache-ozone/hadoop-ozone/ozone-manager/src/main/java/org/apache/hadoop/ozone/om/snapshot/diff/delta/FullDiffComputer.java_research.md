## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/FullDiffComputer.java

Purpose: exhaustive delta strategy that compares relevant SST files in two snapshot DBs and links all files unique to either side, with a fallback to all relevant files if inode-based comparison fails.

Important APIs and types: package-private subclass of `FileLinkDeltaFileComputer`; overrides `computeDeltaFiles`; static helpers `getSSTFileMapForSnapshot` and `getSSTFileSetForSnapshot`.

Control flow: opens both snapshots, obtains their DB locations, collects relevant SST metadata by table and prefix. Primary path compares maps keyed by inode/comparison identity and links only asymmetric files. On `IOException`, it clears results and links every relevant SST from both snapshots using set-based comparison metadata.

State and persistence: produces temporary hard links only. No durable state.

Dependencies and integration: uses `RdbUtil.getSSTFilesWithInodesForComparison`, `RdbUtil.getSSTFilesForComparison`, and `RocksDiffUtils.filterRelevantSstFiles`. Invoked by `CompositeDeltaDiffComputer` for forced diff or fallback.

Risks and test signals: fallback broadens the scan set and may duplicate source paths from both snapshots. Inode metadata can be unavailable on some filesystems. Tests should cover table-prefix filtering, unique-file linking, fallback path, empty diffs, link failures, and correct `SstFileInfo.getFilePath` base path use.
