<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/setup_test.go

## Purpose

This package setup file orchestrates all kernel list cache integration suites. It defines default configs for infinite, delete-dir, finite, and disabled list cache modes, initializes shared clients/environment, and runs the package over static, dynamic, and only-dir mounting modes.

## Important APIs, Types, and Functions

It defines constants `testDirName`, `onlyDirMounted`, and `GKETempDir`; globals `mountFunc`, `mountDir`, `rootDir`, and `testEnv`; struct `env`; `TestMain`; and `overrideFilePathsInFlagSet`. `TestMain` uses setup/test-suite config readers, Cloud Storage client creation, static/dynamic/only-dir mounting utilities, and cleanup helpers.

## Control Flow

When config lacks a `KernelListCache` section, four `ConfigItem`s are created with explicit flags and `Run` selectors. The environment and storage client are initialized, mounted-directory mode is handled early, otherwise the test bucket dir is set up and GKE temp paths are rewritten for GCE. The tests first run with static mounting. If successful, dynamic mounting runs with `mountDir` pointing to `<mount>/<bucket>`. If still successful, only-dir mounting runs with `OnlyDirMountKernelListCache/` and then cleans that prefix. Final cleanup removes the main test directory.

## State and Persistence Behavior

This file owns package-global mutable mount function and mount directory state, which changes between the three execution phases. It also owns shared context, storage client, config pointer, bucket type, and current test directory path.

## Dependencies and Integration Points

It is the integration point for `test_suite.TestConfig`, bucket-type compatibility filtering, static/dynamic/only-dir mounting implementations, and all kernel list cache suite files.

## Risks and Test Signals

Because `m.Run()` is invoked multiple times in one process, package globals must be correctly reset before each phase. Path rewriting must keep log/cache/temp paths valid outside GKE. Success is all selected sub-suites passing in each mounting mode and GCS prefixes being cleaned.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/setup_test.go -->
