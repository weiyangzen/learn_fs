# sources/sync-backup/syncthing/lib/fs/walkfs_test.go

## Purpose
Shared walk tests for symlink handling and Windows directory junction traversal/recursion detection.

## Important APIs, Types, and Functions
`testWalkSkipSymlink`, `createDirJunct`, `testWalkTraverseDirJunct`, and `testWalkInfiniteRecursion`.

## Control Flow
Symlink test creates a target tree and a symlink under a walked directory, then asserts the walker sees the symlink but does not descend. Junction tests create Windows junctions with `cmd /c mklink /J`; one verifies traversal when `OptionJunctionsAsDirs` is set, and another creates a cycle and expects one `ErrInfiniteRecursion` callback.

## State and Persistence Behavior
Mutates temp filesystem trees and Windows junctions. No persistent state beyond test roots.

## Dependencies and Integration Points
Called from `basicfs_test.go` for the basic filesystem. Uses `build` platform flags and `NewFilesystem`.

## Risks
Windows junction tests depend on privileges and command availability. Symlink test skips Windows.

## Test Signals
Important coverage for scanner traversal boundaries: symlinks are not followed, junctions can be traversed, and cycles are detected.
