# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/stat_object_test.go

## Purpose

This file verifies `os.Stat` behavior on read-only mounts for existing files/directories and missing objects.

## Important APIs, Types, and Functions

`statObject` wraps `os.Stat` and returns `os.FileInfo`. Tests cover existing root file, nested files, directory, and subdirectory. `checkIfNonExistentObjectFailedToStat` expects `os.Stat` failure and validates a not-found error. Four negative tests cover missing files and directories at different depths.

## Control Flow

Existing-object tests stat a path and compare returned `Name` and `IsDir` values. Negative tests stat missing paths and call the package not-found validator.

## State and Persistence Behavior

The file only reads metadata from the seeded fixture hierarchy. It does not mutate local or remote state.

## Dependencies and Integration Points

It depends on standard `os.Stat`, setup paths, and fixture constants from the package harness. It complements list/read tests by validating metadata access under read-only and viewer-credential scenarios.

## Risks and Edge Cases

`statObject` logs a test error but still returns `file`, which may be nil if `os.Stat` fails; subsequent use could panic. Negative tests rely on substring matching for "no such file or directory". Directory semantics depend on implicit directory handling and seeded object prefixes.

## Test Signals

Passing indicates metadata lookup works for existing read-only objects and missing paths produce not-found errors. Failures suggest stat-cache, implicit-directory, permissions, or fixture setup regressions.
