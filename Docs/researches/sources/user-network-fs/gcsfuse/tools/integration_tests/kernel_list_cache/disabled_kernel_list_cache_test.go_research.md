<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/disabled_kernel_list_cache_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/disabled_kernel_list_cache_test.go

## Purpose

This suite verifies disabled kernel list cache behavior. With `--kernel-list-cache-ttl-secs=0`, a directory listing should always be refreshed from gcsfuse/GCS rather than reused from the kernel list cache.

## Important APIs, Types, and Functions

`disabledKernelListCacheTest` embeds `suite.Suite` and stores current mount flags. Setup mounts via `setup.MountGCSFuseWithGivenMountWithConfigFunc` using the package `mountFunc` and sets the mount directory. `TestKernelListCache_AlwaysCacheMiss` uses `operations.CreateDirectory`, `operations.CreateFile`, `os.Open`, `Readdirnames`, and `client.CreateObjectInGCSTestDir`.

## Control Flow

The test creates an explicit directory with two mounted files, opens and lists it to populate any kernel-side directory data, closes the directory handle, then creates a third object directly in GCS. It reopens the directory and expects the second listing to contain all three names in order, proving the second read was not served from stale kernel cache.

## State and Persistence Behavior

State spans mounted filesystem entries, a direct GCS object injection, and kernel directory entry cache behavior. `SetupTest` resets `testEnv.testDirPath` for `KernelListCacheTest`; suite teardown unmounts. The test intentionally mutates backing storage outside the mount to observe cache coherency.

## Dependencies and Integration Points

The file depends on package setup for `testEnv`, `mountFunc`, `mountDir`, bucket type, and generated flag sets. It integrates with static, dynamic, only-dir, and mounted-directory modes selected in `setup_test.go`.

## Risks and Test Signals

The assertions assume deterministic listing order from gcsfuse for the created names. If ordering changes, behavior may be correct but test failures would occur. Passing signal is immediate visibility of the third GCS-created object under disabled kernel list cache.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/disabled_kernel_list_cache_test.go -->
