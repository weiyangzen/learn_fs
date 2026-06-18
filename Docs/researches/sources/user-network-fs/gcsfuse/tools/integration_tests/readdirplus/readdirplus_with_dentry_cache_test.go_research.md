# sources/user-network-fs/gcsfuse/tools/integration_tests/readdirplus/readdirplus_with_dentry_cache_test.go

## Purpose

This suite verifies that when readdirplus and dentry cache are enabled, GCSFuse serves `ReadDirPlus` directory listing correctly and avoids extra `LookUpInode` calls during the measured directory read.

## Important APIs, Types, and Functions

`ReaddirplusWithDentryCacheTest` is a `testify/suite` suite with flags, storage client, context, and base name. `SetupSuite` configures the log file and mounts, `SetupTest` creates a per-test directory, teardown preserves logs and unmounts. `TestReaddirplusWithDentryCache` creates a target directory with one file, one empty subdirectory, and one non-empty subdirectory, then calls `fusetesting.ReadDirPlusPicky`.

## Control Flow

The test builds a known directory tree, records start/end timestamps around `ReadDirPlusPicky`, checks the returned entries count, names, directory flags, and modes, then calls `validateLogsForReaddirplus` with `dentryCacheEnabled=true`. That validator requires `ReadDirPlus` logs, rejects `ReadDir` logs, and rejects `LookUpInode` logs in the measured window.

## State and Persistence Behavior

The suite creates GCS-backed objects and directories under `dirForReaddirplusTest/<test name>`. It writes trace JSON logs to a per-suite log file. Directory and inode cache state is intentionally warmed during setup and object creation, and this is part of the expected no-lookup behavior.

## Dependencies and Integration Points

It uses shared `readdirplus` harness state and helpers, `operations` directory/file helpers, `setup.SetUpLogFilePath`, `fusetesting.ReadDirPlusPicky`, and `testify` assertions. It depends on mount flags `--experimental-enable-readdirplus` and `--experimental-enable-dentry-cache`.

## Risks and Edge Cases

The test assumes stable listing order (`emptySubDirectory`, `file`, `subDirectory`) and specific modes. Log-based assertions depend on trace JSON formatting and timestamp windows. If setup no longer warms parent inode cache, `LookUpInode` expectations may need adjustment.

## Test Signals

Success requires correct readdirplus entry metadata and logs showing `ReadDirPlus` but not `ReadDir` or `LookUpInode`. Failures separate data-plane listing issues from control-plane/cache behavior through the log validator.
