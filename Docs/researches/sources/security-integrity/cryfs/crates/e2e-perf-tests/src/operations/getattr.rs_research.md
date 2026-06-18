# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/getattr.rs

## Purpose
This module defines the path/node-handle `getattr` performance counter suite. It measures attributes for root, files, directories, symlinks, and files under nested/deep paths.

## Important APIs, Types, And Functions
Registered cases are `rootdir`, `file_in_rootdir`, `dir_in_rootdir`, `symlink_in_rootdir`, `file_in_nesteddir`, and `file_in_deeplynesteddir`. The operation is `fixture.filesystem.getattr(None)` for root or `getattr(Some(node))` for created objects.

Setup uses `create_file`, `mkdir`, `create_symlink`, and `mkdir_recursive`. The module relies on `AbsolutePath` for symlink targets and deep paths, plus the usual perf-test and action-count types.

## Control Flow
Each non-root case creates the object in setup, then reads its attributes during measurement. Root has no setup and calls `getattr(None)`. Expected counts branch by fixture type for all non-root cases; root expects all zero counters because root attributes are not stored in blobs.

## State And Persistence Behavior
`getattr` is read-only. File, directory, and symlink attribute reads load stores and read blob data but do not write, resize, flush, or store. Directories and symlinks require full reads in root cases; file root with inode cache can avoid `blob_read_all`. Deeper paths add traversal loads for fuse-mt and no-cache fuser.

## Dependencies And Integration Points
The suite compares path/inode cache behavior across generated fixture types. It is the path-handle counterpart to `fgetattr.rs`, and its zero-root expectation documents a special root metadata path in the filesystem implementation.

## Risks And Edge Cases
The tests do not assert returned attributes, only counters. They do not cover missing nodes, stale handles, permission errors, or atime-specific differences. Several expected counts are marked as needing confirmation.

## Test Signals
Key signals are zero root storage access, read-only counters for non-root objects, object-type differences (`blob_read_all` for dir/symlink), and path-depth cache behavior. Any accidental metadata write during `getattr` should be caught.
