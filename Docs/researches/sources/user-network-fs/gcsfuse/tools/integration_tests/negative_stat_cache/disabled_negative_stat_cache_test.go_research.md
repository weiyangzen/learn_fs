<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/disabled_negative_stat_cache_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/disabled_negative_stat_cache_test.go

## Purpose

This suite verifies negative stat cache disabled behavior. When negative metadata cache TTL is zero, a file that was missing should become visible immediately after a same-name object is created directly in GCS.

## Important APIs, Types, and Functions

`disabledNegativeStatCacheTest` stores flags and a per-test directory name. Setup mounts with package `testEnv.mountFunc`, sets mount dir, and creates a randomized test directory. The test uses `os.OpenFile`, `operations.CreateDirectory`, and `client.CreateObjectInGCSTestDir`.

## Control Flow

The test creates an explicit directory, attempts to open `file1.txt` read-only and expects a no-such-file error, creates the object in GCS under the same path, then immediately opens the file again through the mount. With negative stat cache disabled, the second open should query GCS and succeed.

## State and Persistence Behavior

State is a previously cached negative lookup candidate plus a direct GCS object insertion. Randomized `s.testDir` avoids cross-test cache contamination. The successful file handle is closed at the end.

## Dependencies and Integration Points

It depends on the negative_stat_cache package setup for mount configuration and flag sets, plus shared setup/client/operations helpers. It runs in mounted-directory or configured GCE mode.

## Risks and Test Signals

The expected error string includes the path and `no such file or directory`. Passing signal is immediate visibility of a GCS-created object after an initial miss.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/disabled_negative_stat_cache_test.go -->
