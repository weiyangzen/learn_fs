<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/sequential_read_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/sequential_read_test.go

Purpose: Integration suite validating buffered reader behavior for sequential reads, mixed header/footer/body reads, and reads spanning buffer blocks.

Important APIs, types, and functions: `SequentialReadSuite` provides setup/teardown and test cases `TestSequentialRead`, `TestReadHeaderFooterAndBody`, and `TestReadSpanningTwoBlocks`. Top-level `TestSequentialReadSuite` runs the suite for mounted directory or configured flag sets.

Control flow: Suite setup configures logging and mounts gcsfuse. Tests truncate logs, create files of specific sizes, perform direct reads with specific chunk sizes/offsets, validate contents against GCS, parse exactly one buffered-read log entry, and assert no fallback/random seeks for sequential patterns.

State and persistence behavior: Creates bucket objects and reads through mounted files. Logs are truncated per case and parsed after closing handles where needed. Suite unmounts after completion and saves logs on failure.

Dependencies and integration points: Depends on helpers in `helpers_test.go`, `testEnv` from setup, gcsfuse buffered read flags, and integration setup utilities.

Risks and test signals: `O_DIRECT` and block alignment can be environment-sensitive. Header/footer/body test intentionally mixes random-looking reads on one handle but expects no fallback, making it a high-signal regression test for classifier behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/sequential_read_test.go -->
