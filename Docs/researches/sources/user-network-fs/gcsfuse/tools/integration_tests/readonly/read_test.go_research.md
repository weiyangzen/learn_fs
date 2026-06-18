# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/read_test.go

## Purpose

This file verifies that existing files can be read through a read-only mount and non-existent files fail with "no such file or directory".

## Important APIs, Types, and Functions

`checkIfFileReadSucceeded` reads a file with `operations.ReadFile` and compares string content. `TestReadFile`, `TestReadFileFromBucketDirectory`, and `TestReadFileFromBucketSubDirectory` cover seeded files at different depths. `checkIfNonExistentFileFailedToOpen` opens with `os.O_RDONLY|syscall.O_DIRECT` and validates the not-found error. Three tests cover missing files at matching depths.

## Control Flow

Existing-file tests construct paths and compare contents against constants from setup. Missing-file tests attempt direct-read opens and call `checkErrorForObjectNotExist`.

## State and Persistence Behavior

The file reads seeded GCS objects but does not mutate state. Direct I/O open attempts for missing files do not create objects.

## Dependencies and Integration Points

It uses package fixture constants, `operations.ReadFile`, setup permissions, and the package-level not-found validator. It runs under multiple read-only mount and credential configurations.

## Risks and Edge Cases

`checkIfNonExistentFileFailedToOpen` defers `file.Close()` even if open fails and returns a nil file, which can panic. Existing content constants include trailing newlines and must match setup writes exactly. `O_DIRECT` may influence error behavior on some platforms.

## Test Signals

Passing means read-only does not block reads, fixture contents are exact, and missing files surface not-found rather than read-only errors. Failures separate data access regressions from negative path behavior.
