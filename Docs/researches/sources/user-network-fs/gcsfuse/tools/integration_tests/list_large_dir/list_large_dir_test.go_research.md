<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/list_large_dir/list_large_dir_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/list_large_dir/list_large_dir_test.go

## Purpose

This package setup file configures the list-large-directory integration tests. It defines the object-name prefixes and scale constants, initializes the shared environment, and runs static-mount test suites for both kernel-list-cache and metadata-prefetch configurations.

## Important APIs, Types, and Functions

The file defines constants for file, explicit dir, and implicit dir prefixes plus counts of 12,000 files, 100 implicit dirs, and 100 explicit dirs. It defines package globals `directoryWithTwelveThousandFiles`, `mountFunc`, and `testEnv`, plus `env` and `TestMain`.

## Control Flow

`TestMain` parses setup flags, reads config, and creates a default `ListLargeDir` config when needed. The default config has one run selector for `TestListLargeDirWithKernelListCache` with `--kernel-list-cache-ttl-secs=-1` and one for `TestListLargeDirWithoutKernelListCache` with metadata prefetch. It initializes context, storage client, bucket type, and config pointer; delegates mounted-directory runs when requested; sets up the test bucket directory; sets `mountFunc` to static mounting; runs `m.Run`; and exits with the result.

## State and Persistence Behavior

Package state includes a randomized local directory name, shared storage client/context, bucket type, and selected mount function. The test bucket prefix persists only for the test run and is managed by setup utilities and suite-level delete calls.

## Dependencies and Integration Points

It integrates `test_suite` config compatibility, static mounting, Cloud Storage client lifecycle, and the list stress tests in `list_dir_with_twelve_thousand_files_test.go`.

## Risks and Test Signals

The default flag strings include comma-separated flags in the first config entries, so compatibility with `BuildFlagSets` parsing is important. Success is the test package running selected suites against a mounted test bucket without leaking the storage client.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/list_large_dir/list_large_dir_test.go -->
