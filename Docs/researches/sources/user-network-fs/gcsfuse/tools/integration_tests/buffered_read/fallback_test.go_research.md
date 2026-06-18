<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/fallback_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/fallback_test.go

Purpose: Integration suites validating buffered-read fallback behavior when reader creation fails due to block pool limits or access pattern becomes random.

Important APIs, types, and functions: `fallbackSuiteBase` provides suite setup/teardown. `InsufficientPoolCreationSuite` tests no reader creation with insufficient global pool. `RandomReadFallbackSuite` tests random read fallback, small-file no fallback, and random-then-sequential restart. Top-level `TestInsufficientPoolCreationSuite` and `TestRandomReadFallbackSuite` run suites for configured flag sets.

Control flow: Suite setup configures log file, mounts gcsfuse, and sets mount directory. Tests truncate logs, create GCS-backed files, read with `O_DIRECT`, validate read contents against GCS, parse buffered-read logs, and assert fallback/restart/random seek fields.

State and persistence behavior: Creates test files in the mounted bucket, writes/truncates gcsfuse logs, and unmounts after suite. Log parsing is central test state.

Dependencies and integration points: Depends on setup/client/operations utilities, JSON read log parser, `testEnv` initialized by `setup_test.go`, and gcsfuse buffered read flags such as `--read-global-max-blocks`, block sizes, and kernel reader disabling.

Risks and test signals: Tests assert internal log messages/fields, so logging schema changes can fail tests even if behavior is correct. `O_DIRECT` may have platform/filesystem constraints. Strong signals include no log entry when reader creation fails, fallback flag after random reads, and restart after sequential pattern resumes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/buffered_read/fallback_test.go -->
