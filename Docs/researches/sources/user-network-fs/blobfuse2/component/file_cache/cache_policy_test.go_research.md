# sources/user-network-fs/blobfuse2/component/file_cache/cache_policy_test.go

## Purpose

`cache_policy_test.go` validates shared file-cache policy helpers for directory usage and file deletion behavior.

## Important APIs, Types, and Functions

The suite defines `cachePolicyTestSuite`, `SetupTest`, `cleanupTest`, and tests `common.GetUsage`, `getUsagePercentage`, and `deleteFile`.

## Control Flow

Setup initializes a silent logger and creates `cache_path`. Usage tests create a 1 MiB file and assert measured usage is near one MiB or about 25 to 30 percent of a four-MiB max. The zero-max test calls `getUsagePercentage("/", 0)` and asserts it returns a bounded nonnegative value. Deletion tests call `deleteFile` on a deliberately nonexistent suffix and expect no error.

## State and Persistence Behavior

Tests create and remove a local cache directory and a temporary file. They rely on package-level `cache_path` from other file-cache tests.

## Dependencies and Integration Points

It uses `testify`, Blobfuse `common` and `log`, and standard filesystem packages. It indirectly requires the file cache stats collector behavior to be safe in the test environment.

## Risks and Edge Cases

The measured size can vary by filesystem block accounting, so assertions use ranges. The test relies on a shared `cache_path` symbol and could be affected by test order or parallelism.

## Test Signals

Passing tests show usage helpers produce plausible numbers and cache deletion treats missing files idempotently.
