# sources/user-network-fs/gcsfuse/tools/integration_tests/rename_dir_limit/move_dir_test.go

## Purpose

This file validates directory move semantics through GCSFuse, including moving populated and empty directories into non-existing, empty, and non-empty destinations.

## Important APIs, Types, and Functions

Constants define source/destination directory names, file names, expected content, and expected listing counts. `createSrcDirectoryWithObjectsForMoveDirTest` creates a source directory with one file and one subdirectory. `checkIfMovedDirectoryHasCorrectData` validates moved listing and file content. `checkIfSrcDirectoryGetsRemovedAfterMoveOperation` requires source removal. `createDestNonEmptyDirectoryForMoveTest` creates a destination with an existing subdirectory. `checkIfMovedEmptyDirectoryHasNoData` validates empty-directory moves.

## Control Flow

Each test creates a fresh package test directory, builds a source tree, optionally builds destination state, calls `operations.Move`, and validates destination shape plus source removal. Populated-source tests cover move-to-new-path, move-into-empty-directory, and move-into-non-empty-directory. Empty-source tests cover move into non-empty, empty, and non-existing destinations.

## State and Persistence Behavior

The tests create and move GCS-backed directories/objects through the mounted filesystem. Expected final state is source absence and destination presence with either preserved source contents or empty directory content. Existing destination children must remain unaffected.

## Dependencies and Integration Points

It depends on standard `os`, `path`, `operations` helpers for move/create/read/write, and setup test directories. It runs under the rename-dir-limit package harness across static, only-dir, and persistent mounting.

## Risks and Edge Cases

The listing assertions assume deterministic ordering. `log.Fatal` in helper validation exits the process on listing errors. The file focuses on successful move behavior and does not directly assert rename-dir-limit rejection; that is covered in `rename_dir_test.go`.

## Test Signals

Passing means directory moves preserve contents, retain existing destination entries, remove sources, and handle empty directories correctly. Failures indicate recursive rename/move, implicit-directory, or cleanup semantics bugs.
