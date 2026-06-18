
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/tempdir.rs

## Purpose
`TempDirBlockStore` is a testutils helper that runs `OnDiskBlockStore` inside a temporary directory and ties directory cleanup to the store lifetime.

## Important APIs, Types, and Functions
- `TempDirBlockStore::new()` creates a tempdir with prefix `cryfs-tempdir-blockstore` and constructs an `OnDiskBlockStore` at that path.
- Contains `_tempdir: TempDir` and `underlying_store: AsyncDropGuard<OnDiskBlockStore>`.
- Implements all low-level reader/deleter/optimized-writer methods by delegating to the on-disk store.
- Async drop explicitly drops the underlying store before the tempdir field is dropped.

## Control Flow
Construction creates the tempdir, clones its path, and then creates the on-disk backend. Method calls are pass-through. Field order matters: the comment notes the underlying store should drop before the tempdir disappears.

## State and Persistence Behavior
Blocks persist only for the lifetime of the tempdir. Directory cleanup is managed by `tempfile::TempDir` after async-drop completes.

## Dependencies and Integration Points
Wraps `OnDiskBlockStore` and is exported under `test` or `testutils`. Useful for tests that need real filesystem behavior without managing paths.

## Risks and Edge Cases
- `new()` panics if tempdir creation fails.
- If async-drop is not called, underlying store cleanup may be skipped, though `TempDir` still removes the directory on drop.

## Test Signals
Runs the full common low-level blockstore test suite with the tempdir-backed on-disk implementation.
