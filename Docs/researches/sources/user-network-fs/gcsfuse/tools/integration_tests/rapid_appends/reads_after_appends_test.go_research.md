# sources/user-network-fs/gcsfuse/tools/integration_tests/rapid_appends/reads_after_appends_test.go

Purpose: Verifies sequential and random reads after rapid appends for single-mount and dual-mount setups, with and without metadata cache.

Important APIs/types/functions: `readAndVerifyFunc` abstracts read validation. `readSequentiallyAndVerify` reads whole content with `operations.ReadFileSequentially`. `readRandomlyAndVerify` performs up to ten random `ReadAt` calls and compares slices. Suite methods `runAppendAndReadTest` implement single and dual mount loops. Runner functions instantiate suites with metadata-cache flags.

Control flow: single-mount tests append twice through one handle and immediately verify the current full content after each append. Dual-mount tests append through `getAppendPath` and read through primary mount; with metadata cache enabled, subsequent reads first see cached old size, wait for TTL/flush, then see updated size.

State/persistence: Suite `fileContent` is the expected byte source. File handles are opened with append plus direct I/O. Dual-mount cases intentionally expose stale metadata state until cache expiry.

Dependencies/integration: Uses rapid-appends base suite, setup random data, operation read helpers, `math/rand/v2`, and testify suite.

Risks/test signals: Random reads are nondeterministic but bounded. Time sleeps depend on `metadataCacheTTLSecs` and `operations.WaitDurationAfterFlushZB`. Passing signals read paths respect append updates and metadata-cache staleness rules.
