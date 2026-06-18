# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/inactive_stream_timeout/setup_test.go

Purpose: package setup and log parsing helpers for inactive read stream timeout tests. It configures enabled/disabled timeout flag sets and runs across static, dynamic, and only-dir mounts.
Important APIs/types/functions: constants for test dir, only-dir prefix, file/chunk sizes, default timeout, log paths, retry timing; `env`; globals `testEnv`, `mountFunc`, `mountDir`, `rootDir`; `mountGCSFuseAndSetupTestDir`; `doesNotHaveInactiveReaderClosedLogLineInLogFile`; `hasInactiveReaderClosedLogLineInLogFile`; and `TestMain`.
Control flow: setup reads config or populates default enabled/disabled timeout configs with JSON log files, initializes storage client/environment, handles mounted-directory mode, otherwise sets up test bucket, overrides paths, runs static tests, then dynamic, then only-dir if successful, and cleans up GCS prefixes.
State and persistence: test state includes JSON gcsfuse log files, GCS objects under `inactiveReadTimeout`, mounted directories, and only-dir prefix. Log helpers parse timestamps to detect close-reader messages within time windows.
Dependencies and integration points: uses `read_logs.ParseJsonLogLineIntoLogEntryStruct`, storage client helpers, static/dynamic/only-dir mounting, and operations retry helper in tests.
Risks and edge cases: log assertions depend on JSON log format and timestamp bounds. Fixed sleeps and retry windows can be flaky under slow logging. Only enabled suite is in this work item, but config also references disabled suite in another file.
Test signals: setup supports log-file path rewriting and mount-mode coverage; helper success/failure indicates whether inactive-reader close messages appear in the expected window.
