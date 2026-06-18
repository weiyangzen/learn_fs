<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/background_unix_test.go -->
# sources/sync-backup/restic/internal/terminal/background_unix_test.go

## Purpose
Tests Unix background-process detection against the controlling terminal when one exists.

## Important APIs and Control Flow
`TestIsProcessBackground` opens `/dev/tty`, skips if unavailable, calls `isProcessBackground`, and asserts no error. Control flow avoids asserting foreground/background status because that depends on the test runner.

## State, Persistence, Dependencies, and Integration
State is the opened tty descriptor. Dependencies are OS terminal availability and shared test helpers.

## Risks and Test Signals
The test catches syscall integration failures but not actual background-job transitions.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/terminal/background_unix_test.go -->
