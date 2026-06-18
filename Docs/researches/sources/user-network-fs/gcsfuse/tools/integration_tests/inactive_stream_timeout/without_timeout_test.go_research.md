<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/inactive_stream_timeout/without_timeout_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/inactive_stream_timeout/without_timeout_test.go

## Purpose

This suite verifies that the inactive stream timeout feature does not close a reader when the timeout is disabled. It mounts gcsfuse using the package's inactive-stream test harness, opens a file through the mount, performs a small read, waits longer than the default timeout window, and asserts that the gcsfuse log does not contain the inactive-reader close line for that object.

## Important APIs, Types, and Functions

`timeoutDisabledSuite` embeds `suite.Suite` and carries mount flags, a `storage.Client`, `context.Context`, and test metadata. `SetupSuite` calls `setup.SetUpLogFilePath` and `mountGCSFuseAndSetupTestDir`; `TearDownSuite` unmounts through `setup.UnmountGCSFuseWithConfig`; `TearDownTest` saves logs on failure. `TestNoReaderCloser` uses `client.SetupFileInTestDirectory`, `operations.OpenFileAsReadonly`, `ReadAt`, and `doesNotHaveInactiveReaderClosedLogLineInLogFile`. `TestTimeoutDisabledSuite` chooses mounted-directory execution or iterates `setup.BuildFlagSets`.

## Control Flow

For each flag set, the suite configures log paths, mounts, creates a random object under `kTestDirName`, opens it read-only, reads `kChunkSizeToRead` at offset zero, records the time, sleeps for twice `kDefaultInactiveReadTimeoutInSeconds` plus a buffer, then scans logs between the read and wait end time. The expected path is the object path relative to the test directory.

## State and Persistence Behavior

State persists in the mounted filesystem, the backing GCS object created before the read, and the gcsfuse log file. The file handle remains open until deferred close. The test intentionally depends on the absence of background reader cleanup log state after a long idle period.

## Dependencies and Integration Points

It depends on the package-level inactive stream timeout setup variables and helpers, Cloud Storage client APIs, shared setup/mounting utilities, and Testify suite/require. It integrates with GKE mounted-directory mode and normal test-bucket flag-set mode.

## Risks and Test Signals

The test is time-sensitive and log-string-sensitive. A slow system is acceptable because the assertion is negative over a recorded interval, but log format changes or helper timestamp parsing changes can cause false failures. Passing signal is no inactive reader close log while the handle remains idle past the default timeout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/inactive_stream_timeout/without_timeout_test.go -->
