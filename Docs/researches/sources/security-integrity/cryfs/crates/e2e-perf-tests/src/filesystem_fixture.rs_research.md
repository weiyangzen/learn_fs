# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_fixture.rs

## Purpose
Builds the full CryFS blockstore/blobstore/filesystem stack for operation-count tests and benchmarks, inserting tracking wrappers at every relevant layer.

## Important APIs, types, and functions
- Constants `NUM_CHILDREN_PER_INNER_NODE`, `BLOCKSIZE_BYTES`, `NUM_BYTES_FOR_THREE_LEVEL_TREE`, and `MY_CLIENT_ID`.
- `ActionCounts` aggregates blobstore, high-level blockstore, and low-level blockstore counts.
- `FilesystemFixture<B, FS>` owns filesystem, tracked stores, blobstore, and temp local state.
- `create_filesystem`, `create_uninitialized_filesystem`, store/device construction helpers, `reset_counts`, `totals`, cache reset hooks, and `config`.

## Control flow
Fixture creation wraps a supplied low-level blockstore in tracking/shared/locking layers, computes overhead and config blocksize, creates a tracked blobstore, creates a CryFS device through `make_device`, then constructs the selected `FilesystemDriver`. `create_filesystem` additionally calls `init` and clears blobstore cache. Drop destroys the filesystem inside the current Tokio runtime.

## State and persistence behavior
Filesystem data lives in the supplied blockstore; local state lives in a temp directory. Tracking wrappers accumulate counts until reset. Config uses fixed root blob, encryption key, cipher, filesystem id, format version, and client id for reproducibility.

## Dependencies and integration points
Integrates blobstore, low/high-level blockstores, blockstore stack setup, config/local state, runner device creation, rustfs atime behavior, async drop wrappers, and concrete filesystem drivers.

## Risks and edge cases
Manual overhead calculation must match actual blockstore overhead; an assertion guards drift. Drop assumes a Tokio runtime is active. Cache reset behavior is carefully tuned and can deadlock if open files prevent cache unloading.

## Test signals
Operation modules call `totals` and compare `ActionCounts`; fixture assertions catch overhead mismatch and unexpected integrity violations.
