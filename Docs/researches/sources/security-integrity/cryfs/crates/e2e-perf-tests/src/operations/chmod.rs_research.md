# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/chmod.rs

## Purpose
Defines performance tests/benchmarks for `chmod` on files and directories at several path depths.

## Important APIs, types, and functions
- Invokes `perf_test!(chmod, [file_in_rootdir, dir_in_rootdir, file_in_nesteddir, file_in_deeplynesteddir])`.
- Scenario functions build fixtures, set up target nodes, execute `filesystem.chmod`, and declare expected `ActionCounts`.
- Uses `FixtureType` to vary expected counts for fuser cached, fuser uncached, and fuse-mt drivers.

## Control flow
Each scenario creates a filesystem, creates the relevant target in setup, resets caches through the test driver, performs chmod with a file or directory mode flag, and checks blobstore/high-level/low-level operation counters.

## State and persistence behavior
The operation mutates mode metadata on the target node and writes affected blobs/blocks. Expected counts reflect whether parent/path nodes are cached and how deep the target is.

## Dependencies and integration points
Uses the generic `FilesystemDriver`, `TestDriver`, path helpers, `Mode`, and count structs from blobstore/blockstore layers. It is included in both tests and the all-operations benchmark entry.

## Risks and edge cases
Many expected counts carry TODOs, meaning they encode observed behavior that may not yet be fully justified. Path-depth and cache-model changes will require careful count updates.

## Test signals
Signals are successful chmod execution and exact `ActionCounts` matches for root file, root directory, nested file, and deeply nested file scenarios across fixture types.
