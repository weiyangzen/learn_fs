# sources/user-network-fs/gcsfuse/tools/integration_tests/readdirplus/readdirplus_without_dentry_cache_test.go

## Purpose

This suite verifies readdirplus behavior when dentry cache is not enabled. It expects `ReadDirPlus` listing correctness and confirms lookup calls occur for parent and entries.

## Important APIs, Types, and Functions

`ReaddirplusWithoutDentryCacheTest` mirrors the dentry-cache-enabled suite. Its core test creates the same directory structure and calls `fusetesting.ReadDirPlusPicky`, then validates entries and log behavior through `validateLogsForReaddirplus` with `dentryCacheEnabled=false`.

## Control Flow

Setup configures logging and mounting. The test creates `target_dir`, a file, an empty subdirectory, and a subdirectory containing one file. It records the `ReadDirPlusPicky` time window, verifies the three direct entries, and validates logs. With dentry cache disabled, the validator requires `ReadDirPlus`, rejects plain `ReadDir`, and requires `LookUpInode`.

## State and Persistence Behavior

State is a GCS-backed test tree and trace log file. Unlike the cache-enabled case, lookup behavior is expected during the measured read because dentries are not cached.

## Dependencies and Integration Points

It depends on the shared readdirplus setup, GCS client helpers, operations helpers, `fusetesting`, and the package config item that enables readdirplus without enabling dentry cache.

## Risks and Edge Cases

The same ordering, mode, and log-format assumptions apply as in the cache-enabled suite. The required `LookUpInode` signal can be sensitive to implementation changes that prefetch or cache dentries through another path even when the explicit dentry cache flag is absent.

## Test Signals

Passing signal is correct entry metadata plus logs that show `ReadDirPlus`, do not show `ReadDir`, and do show `LookUpInode`. This distinguishes readdirplus correctness from dentry-cache optimization.
