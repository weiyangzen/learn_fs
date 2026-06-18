<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/terminate_signal_test.go -->
# sources/sync-backup/kopia/cli/terminate_signal_test.go

## Purpose
Tests that an external server process exits cleanly when sent SIGTERM.

## Important APIs, Types, And Functions
`TestTerminate` uses an executable runner, creates a filesystem repository, starts `server start --address=localhost:0 --insecure`, sends SIGTERM through the test runner interrupt hook, and requires `wait()` to return nil.

## Control Flow
The test exercises real process signal handling rather than in-process simulated Ctrl-C.

## State And Persistence Behavior
Persistent test state is a temporary repository. Runtime state includes a started server process and parsed server parameters.

## Dependencies And Integration Points
Integrates server start, repository creation, process runner, OS signals, and graceful shutdown handling in server/config code.

## Risks And Edge Cases
Platform behavior depends on SIGTERM support and process startup timing. It uses insecure server mode to avoid TLS/auth setup.

## Test Signals
Strong signal for termination callbacks and HTTP server shutdown. It does not cover SIGHUP reload or stdin-close shutdown.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/terminate_signal_test.go -->
