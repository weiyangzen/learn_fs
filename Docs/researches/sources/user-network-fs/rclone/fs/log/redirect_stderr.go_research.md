# sources/user-network-fs/rclone/fs/log/redirect_stderr.go

## Purpose
`redirect_stderr.go` is the fallback stderr-redirection implementation for platforms without Unix or Windows support in the other build-tagged files.

## Important APIs, types, and functions
The single function is `redirectStderr(f *os.File)`, compiled for a narrow set of non-Windows, non-common-Unix platforms. It logs that stderr cannot be redirected.

## Control flow
When file logging without rotation is configured, `InitLogging` calls `redirectStderr`. On these platforms the function emits an error through rclone logging and leaves stderr unchanged.

## State and persistence behavior
No state is changed except the emitted log. Stderr remains connected to its original destination.

## Dependencies and integration points
The file depends on `os` and rclone `fs.Errorf`. It shares a function signature with Unix and Windows implementations selected by build tags.

## Risks and edge cases
Panic output may not be captured in the configured log file on these platforms. Because this implementation only logs an error, callers continue running with reduced crash-log capture.

## Test signals
No direct tests are present; platform build coverage verifies selection.

Source-read signal: reviewed complete local file (16 lines). Functions/methods observed: `redirectStderr`.
