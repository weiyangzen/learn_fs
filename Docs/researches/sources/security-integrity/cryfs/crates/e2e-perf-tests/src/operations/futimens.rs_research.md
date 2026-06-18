# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/futimens.rs

## Purpose
This module defines the `futimens` performance counter suite for updating atime and mtime through an open file handle. It covers root, nested, and deeply nested files, each with optional release after the timestamp update.

## Important APIs, Types, And Functions
The registered cases are `file_in_rootdir`, `file_in_nesteddir`, and `file_in_deeplynesteddir` for `CLOSE_AFTER=false` and `true`. The test constructs deterministic timestamps from `SystemTime::UNIX_EPOCH + Duration::from_secs(1000/2000)` and calls `filesystem.futimens(file.clone(), &file_handle, Some(atime), Some(mtime))`.

The module imports `FilesystemDriver as _` to bring trait methods into scope, `maybe_close`, `SystemTime`, `Duration`, path types, and the standard action-count types.

## Control Flow
Setup creates and opens a file, optionally under parent directories. The measured phase computes atime and mtime, updates them through `futimens`, and conditionally releases the handle. Expected counts use `close_after` and fixture type branches.

## State And Persistence Behavior
Timestamp update is a metadata mutation on an open file. Without close, expected write/resize/flush/store counters are mostly absent, suggesting dirty metadata remains buffered. With close, release adds blob resize/write/flush, high-level `blob_data_mut` and `store_flush_block`, and low-level `store`. Path depth affects no-cache fuser load/read counts.

## Dependencies And Integration Points
This suite interacts with open-handle timestamp update semantics and the shared release helper. Although the macro runs all atime behavior modes, the expected counts ignore `_atime_behavior`, so any atime mode-specific timestamp side effect is expected not to change these counters.

## Risks And Edge Cases
Only both atime and mtime set to concrete values are covered. The suite does not test `None` values, ctime behavior, directories, symlinks, invalid handles, time precision, or values before epoch. Expected counts include TODO uncertainty about fuser no-cache work.

## Test Signals
Signals are the absence/presence of persistence counters around `CLOSE_AFTER`, deterministic metadata update loads, and path-depth overhead. Regressions in timestamp buffering or release flushing should change `blob_write`, `blob_resize`, `blob_flush`, `blob_data_mut`, `store_flush_block`, or low-level `store`.
