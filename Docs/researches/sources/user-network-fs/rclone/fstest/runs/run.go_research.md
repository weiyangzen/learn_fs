
# sources/user-network-fs/rclone/fstest/runs/run.go

Purpose: `run.go` executes one configured integration-test command, optionally retries failing leaf tests, and feeds results back to `test_all`.

Important APIs/types/functions: `RunOpt` carries global execution flags. `Run` stores backend/remote/package config plus command, trial, output, failed tests, and log names. `Runs` implements sorting. Helpers include `testsToRegexp`, `findFailures`, `nextCmdLine`, `trial`, `GOPATH`, binary path/name helpers, `MakeTestBinary`, `RemoveTestBinary`, `Init`, `Logs`, `FailedTestsCSV`, `Run`, and `toShell`.

Control flow: `Run.Init` builds either `go test` or precompiled test-binary argv with timeout, remote, verbosity, fast-list, short, size-limit, and run regexp. `trial` starts a testserver for the remote, runs the command in the test package directory, tees output to a log and buffer, parses failures, and marks pass/fail. `Run` repeats trials up to `MaxTries`, narrowing retries to failed leaf tests with `-test.run`.

State/persistence: writes per-trial logs into the report log directory and may build/delete `.test` binaries in package directories. It uses global `oneOnly` mutexes for backends marked exclusive.

Dependencies/integration: integrates with `testserver.Start`, Go `exec`, rclone logging/config, and package paths from `runs.Config`. Failure parsing relies on standard `go test -v` output.

Risks: regex parsing can miss non-standard failure output or setup failures without `--- FAIL` lines. `toShell` is for display only and quotes minimally. Precompiled binaries modify source package directories during the run.

Test signals: paired with `run_test.go`, especially for retry regexp construction and live `go test -run` selection behavior.
