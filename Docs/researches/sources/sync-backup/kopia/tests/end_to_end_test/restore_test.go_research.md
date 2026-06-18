# sources/sync-backup/kopia/tests/end_to_end_test/restore_test.go

## Purpose
Comprehensive restore end-to-end tests for command aliases, progress reporting, object/snapshot/path addressing, archive output modes, overwrite policies, symlinks, permissions, single-file roots, sparse files, and in-place restore.

## Important APIs, Types, and Functions
Constants define Windows name and expected permissions. `fakeRestoreProgress` records progress callbacks. Major tests are `TestRestoreCommand`, `TestSnapshotRestore`, `TestRestoreSymlinkWithoutTarget`, `TestRestoreSymlinkWithNonSymlinkOverwrite`, `TestRestoreSnapshotOfSingleFile`, `TestSnapshotSparseRestore`, `TestSnapshotRestoreByPath`, and `TestRestoreByPathWithoutTarget`. Helpers include `compareDirs`, `compareDirsWithChange`, `verifyFileSize`, `verifyFileMode`, and archive validators for zip/tar/tgz.

## Control Flow
The tests create repositories and source trees, snapshot them, restore by snapshot ID/root object/subpath/source path, compare restored filesystem hashes, exercise overwrite-denial and skip-existing/delete-extra flags, generate archive outputs with auto-detected and forced modes, test symlink edge cases, restore single-file snapshots with conflicting attribute histories, verify sparse-file logical/physical sizes across many hole/data layouts, and restore in-place by source path.

## State and Persistence Behavior
Writes real source and restore trees, repository snapshots, archive files, symlinks, chmod changes, sparse files, and progress state injected into the in-process CLI app. Some tests intentionally alter source files between snapshots to test attribute resolution.

## Dependencies and Integration Points
Integrates CLI restore/snapshot commands, `snapshot/restore` progress, `fshasher`, `diff`, `localfs`, sparse-file stat helpers, archive libraries, `testdirtree`, and `clitestutil`.

## Risks
OS-specific behavior is significant: Unix permissions are skipped on Windows, sparse files are Linux-only, one arm64 sparse case is skipped, and restore idempotency is skipped on Windows. Archive validation checks structural validity but not complete archive contents. Progress injection depends on `runner.CustomizeApp`.

## Test Signals
Signals include correct restore failure from empty/nonexistent IDs, multiple progress updates and final flush, byte-for-byte tree equivalence, overwrite flag enforcement, skipped existing files, delete-extra cleanup, valid archive generation, directory mode forced for `.zip` path with `--mode=local`, symlink restoration/failure behavior, single-file destination semantics, consistent-attribute conflict behavior, sparse physical allocation preservation, and path-based latest restore.
