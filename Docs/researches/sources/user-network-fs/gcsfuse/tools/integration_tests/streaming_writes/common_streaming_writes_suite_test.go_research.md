# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/common_streaming_writes_suite_test.go

## Purpose

Defines shared suite state and helper assertions for streaming-write tests. The common suite supplies a unique test directory, a reusable 5 MiB payload, and a `ReadAt` validation helper used by local-file and empty-GCS-file test suites.

## Important APIs, control flow, and dependencies

`StreamingWritesSuite` stores the active file handle, file name, mounted file path, payload, and a `test_suite.TestifySuite` bridge. `SetupSuite` calls `setup.SetupTestDirectory` and generates data with `setup.GenerateRandomString`. `TearDownSuite` saves the gcsfuse log on failure. `validateReadCall` performs `ReadAt` at offset zero and asserts byte count and content with testify `require` and `assert`.

## State, persistence, dependencies, and integration points

This suite relies on package-level `testEnv` from streaming-writes setup and is embedded by the local-file and empty-GCS-file suites. The payload size crosses multiple one MiB streaming blocks, so read/write tests exercise buffered state before and after upload.

## Risks and test signals

Because the same embedded suite is reused by many test files, stale `f1`, `fileName`, or `filePath` state would cross-contaminate tests if concrete suites failed to recreate files in `SetupTest` and `SetupSubTest`. The direct signal is exact in-handle readback before GCS validation.
