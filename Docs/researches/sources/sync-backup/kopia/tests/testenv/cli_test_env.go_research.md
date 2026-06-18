<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/cli_test_env.go -->
# sources/sync-backup/kopia/tests/testenv/cli_test_env.go

This file defines `CLITest`, the high-level test environment for Kopia CLI tests. It owns a run context, temp repo/config directories, runner, fixed args, environment map, default repo-create flags, and log-output controls.

Core APIs run commands and assert outcomes: `RunAndExpectSuccess`, `RunAndExpectFailure`, `RunAndExpectSuccessWithErrOut`, `RunAndVerifyOutputLineCount`, `RunAndProcessStderr`, and async stderr variants. `Run` builds final args, starts the configured runner, concurrently reads stdout/stderr, waits, asserts expected success/failure, and returns lines. It also provides `TweakFile`, `SetLogOutput`, and `NotificationsSent`.

State includes per-test config/repo dirs and process env overrides such as `KOPIA_PASSWORD`. Dependencies are `testlogging`, `testutil`, notification capture, and runner implementations. Risks include scanner token limits for huge output, goroutine ordering around stderr processing, random file corruption on empty files, and broad logging of environment values. This file is a core integration-test utility.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/testenv/cli_test_env.go -->
