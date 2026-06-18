# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/interface.rs

## Purpose
Defines the common async filesystem driver abstraction used by both in-process performance tests and mounted benchmarks.

## Important APIs, types, and functions
- `FilesystemDriver: AsyncDrop + Debug`.
- Associated `NodeHandle` and `FileHandle` types.
- `new` accepts a fully constructed `CryDevice` stack.
- Async methods cover initialization, cache reset, namespace operations, metadata operations, open file operations, read/write, statfs, rename, and fsync.
- Default `mkdir_recursive` builds nested directories using repeated `mkdir`.

## Control flow
Test operation modules call this trait uniformly. Implementations translate abstract node handles into high-level paths, low-level inodes, or real mounted paths.

## State and persistence behavior
The trait owns no state but defines lifecycle hooks: `init`, `destroy`, `reset_cache_after_setup`, and `reset_cache_after_test`. These hooks determine what remains cached when operation counts are measured.

## Dependencies and integration points
Central contract between `FilesystemFixture`, test drivers, operation modules, and concrete fuser/fuse-mt/mounting drivers.

## Risks and edge cases
`Option<NodeHandle>` represents root; this is repeatedly TODO-noted as less explicit than a root handle. Implementations must keep operation semantics equivalent despite different handle models.

## Test signals
All operation perf tests compile against this trait and compare behavior/counts across implementations.
