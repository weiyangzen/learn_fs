# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/open.rs

## Purpose
This file defines e2e performance counter tests and benchmarks for opening existing files. It measures the cost of `open` in the root directory, a nested directory, and a deeply nested directory, with each case parameterized by whether the file handle is immediately released after opening.

## Important APIs, types, and functions
- Registers six macro-expanded cases through `perf_test!`: `in_rootdir::<false/true>`, `in_nesteddir::<false/true>`, and `in_deeplynesteddir::<false/true>`.
- The const generic `CLOSE_AFTER` controls whether `maybe_close` calls `FilesystemDriver::release` after `FilesystemDriver::open`.
- Setup uses `create_file`, `mkdir`, and `mkdir_recursive` to create the target file and returns the file node handle.
- Expected counts branch on `FixtureType` and use a local `close_after` integer multiplier.

## Control flow
Each test creates a filesystem, creates an existing file at the target depth, resets setup effects, opens the file by node handle, and optionally releases it. The root case uses a file under `None`; nested cases create one or more parent directories and then create the file under the returned parent handle.

## State and persistence behavior
`open` itself should not create or modify file data. When the inode is already cached under `FuserWithInodeCache`, opening without release is expected to require no blobstore or blockstore operations. Fuse-mt and fuser without inode cache load path/file metadata. When `CLOSE_AFTER` is true, release adds flush activity (`blob_flush`, `store_flush_block`, and additional loads/reads), even though no file data was changed.

## Dependencies and integration points
The file depends on `FilesystemDriver` for `open`, setup helpers, and `release` via `maybe_close`. It uses `TestDriver`/`TestReady` for harness composition, `FixtureType` for expected-count selection, and `cryfs_utils::path` for valid path components. It is sensitive to driver implementation details: fuser without inode cache performs more lookup work because its node handles do not retain the resolved node as aggressively.

## Risks and observations
Most comments question whether the counts are expected. The largest risk is that the suite encodes current cache behavior rather than a stable interface contract. Changes to node-handle caching, file-handle release semantics, or flush behavior will break counts even if user-visible open behavior remains correct. The optional release path also means the same test name family measures a mixed cost of open plus close.

## Test signals
The suite verifies that cached fuser opens can be metadata-free, that path depth increases lookup cost for fuse-mt and fuser without cache, and that release consistently adds flush/load overhead. Benchmarks generated under the `benchmark` feature provide timing signals for the same cases.
