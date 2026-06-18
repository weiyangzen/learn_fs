# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/list_objects_test.go

## Purpose

This file verifies that read-only mounts still allow directory listing and expose the expected seeded objects.

## Important APIs, Types, and Functions

`TestListObjectsInBucket` lists the read-only test root and expects the `Test` directory and `Test1.txt` file. `TestListObjectsInBucketDirectory` lists the nested `Test` directory and expects `a.txt` and `b`.

## Control Flow

Each test calls `os.ReadDir`, checks the number of entries, then checks names and `IsDir` flags by index.

## State and Persistence Behavior

The tests read fixture state created by `createTestDataForReadOnlyTests`. They do not mutate the filesystem. Listing order is treated as stable and part of the assertion.

## Dependencies and Integration Points

It depends on fixture constants, `setup.MntDir`, and standard `os.ReadDir`. It complements the mutation-denial tests by proving read/list operations remain available under read-only flags and viewer credentials.

## Risks and Edge Cases

The tests assume deterministic ordering from `os.ReadDir`, which is sorted by filename in Go, matching expected names. They use `log.Fatal` on read errors, which exits the test process rather than failing only the current test. The fixture object count must remain aligned with setup.

## Test Signals

Passing indicates directory listing works under read-only mode and object/directory classification is correct. Failures suggest fixture setup, implicit directory, read permission, or list behavior regressions.
