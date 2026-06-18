# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/fchmod.rs

## Purpose
This module defines the `fchmod` performance counter suite for changing permissions through an open file handle. It covers root, nested, and deeply nested files, with and without releasing the file handle after the operation.

## Important APIs, Types, And Functions
The `perf_test!(fchmod, [...])` registration expands six cases: each of `file_in_rootdir`, `file_in_nesteddir`, and `file_in_deeplynesteddir` is instantiated for `CLOSE_AFTER = false` and `true`. Each case uses `create_and_open_file`, then calls `filesystem.fchmod(file.clone(), &file_handle, Mode::from(0o644).add_file_flag())`.

The generic helper `maybe_close::<CLOSE_AFTER, _>` conditionally calls `release`. The module depends on `Mode`, `AbsolutePath`, `PathComponent`, the fixture driver traits, and the three action-count types.

## Control Flow
Setup creates a file and retains both the node handle and file handle. Nested cases create parent directories first. The measured phase updates permissions through `fchmod`, then optionally releases the open handle. Expected counts derive a local `close_after` integer so release-related persistence and flush work can be folded into the same expectation expression.

## State And Persistence Behavior
The permission update is a metadata mutation associated with an open handle. Without close, the expected `blob_write`, `blob_resize`, `blob_flush`, `blob_data_mut`, `store_flush_block`, and low-level `store` are often zero, indicating much of the dirty state may remain buffered. With close, release adds resize/write/flush/store work. Path depth only materially changes no-cache fuser lookup/read counts.

## Dependencies And Integration Points
This suite validates both fuser and fuse-mt implementations through `perf_test!`. It specifically exercises the file-handle API surface rather than path-only chmod. It integrates with `maybe_close`, which is shared across other open-handle operation tests.

## Risks And Edge Cases
Only a file mode is tested; directory modes, symlinks, invalid mode bits, closed handles, and permission failures are absent. The expectations assume release is the only close-related persistence point. Several TODO comments flag uncertainty around fuser without inode cache doing additional work.

## Test Signals
The main signals are the delta between `CLOSE_AFTER=false` and `true`, and fixture-specific load/read multipliers. A regression in open-handle metadata caching, release flush behavior, or inode-cache path reuse should change these counters.
