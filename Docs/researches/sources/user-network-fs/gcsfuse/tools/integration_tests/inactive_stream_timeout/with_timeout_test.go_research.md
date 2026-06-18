# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/inactive_stream_timeout/with_timeout_test.go

Purpose: tests active behavior when `--read-inactive-stream-timeout` is enabled. It verifies idle readers are closed after timeout and remain open when accessed within timeout.
Important APIs/types/functions: `timeoutEnabledSuite` with flags/storage/context/base test name; lifecycle methods; `TestReaderCloses`; `TestReaderStaysOpenWithinTimeout`; and `TestTimeoutEnabledSuite`.
Control flow: suite setup configures log file path and mounts. `TestReaderCloses` creates a 10 MiB object, opens it, reads a 128 KiB chunk, waits over twice the timeout, polls logs for the inactive-reader close message, then reads again to prove a new reader can be created. `TestReaderStaysOpenWithinTimeout` reads, sleeps half the timeout, reads again, and asserts no close log occurred in between.
State and persistence: state includes open file handles, backing GCS object, gcsfuse JSON log file, and reader lifecycle inside gcsfuse. File handles are closed by defer.
Dependencies and integration points: depends on setup helpers in `setup_test.go`, `client.SetupFileInTestDirectory`, `operations.OpenFileAsReadonly`, `operations.RetryUntil`, and package config flag sets for HTTP and gRPC.
Risks and edge cases: log timing windows use `time.Now()` around reads/sleeps, so clock skew with log timestamps or delayed flushing can affect results. Sleeps intentionally include buffers to reduce flake.
Test signals: close log found after idle interval, absent before timeout, and subsequent read success validate inactive stream cleanup without breaking file handles.
