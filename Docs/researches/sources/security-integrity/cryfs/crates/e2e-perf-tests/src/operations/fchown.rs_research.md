# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/fchown.rs

## Purpose
This module defines the `fchown` performance counter suite for changing owner and group through an open file handle. It mirrors the `fchmod` matrix but uses uid/gid metadata instead of mode bits.

## Important APIs, Types, And Functions
The six registered cases instantiate `file_in_rootdir`, `file_in_nesteddir`, and `file_in_deeplynesteddir` for both close behaviors. Each setup creates and opens a file, then the test calls `filesystem.fchown(file.clone(), &file_handle, Some(Uid::from(1000)), Some(Gid::from(1000)))` and optionally `maybe_close`.

Imports include `Uid`, `Gid`, `AbsolutePath`, `PathComponent`, `FixtureType`, and the instrumented action counters.

## Control Flow
The measured operation always runs against an existing open file. Parent directory setup varies by path depth. Expected count closures compute `close_after` and branch on `FixtureType`. Deep no-cache fuser cases have the highest load/read counts because resolving stored path-backed node handles traverses more ancestors.

## State And Persistence Behavior
`fchown` mutates file metadata. Like `fchmod`, most write/resize/flush/store counts are tied to optional release, suggesting dirty metadata is retained on the open handle until close in these measured scenarios. The call itself still loads and reads the file metadata. `blob_num_bytes` is used as a size/header signal and increases for no-cache fuser plus close.

## Dependencies And Integration Points
The suite is part of the generated `perf_test!` infrastructure and uses shared `maybe_close`. It is a direct consumer of the `FilesystemDriver` file-handle ownership API and the CryFS RustFS uid/gid wrapper types.

## Risks And Edge Cases
Only setting both uid and gid is tested. The suite does not cover `None` uid/gid combinations, unchanged ownership, invalid handles, root, symlink semantics, or authorization errors. The many TODO comments mean expected counts are empirical and may need redesign if the driver caching model changes.

## Test Signals
Useful signals are release-driven persistence counters, fixture-specific metadata loads, and depth-driven no-cache overhead. Any change to ownership update durability or handle release flushing should alter `blob_write`, `blob_resize`, `blob_flush`, `blob_data_mut`, `store_flush_block`, and low-level `store`.
