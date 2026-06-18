# sources/user-network-fs/rclone/fs/log/redirect_stderr_unix.go

## Purpose
`redirect_stderr_unix.go` redirects process stderr to the configured log file on supported Unix-like platforms so panics and runtime diagnostics are captured.

## Important APIs, types, and functions
The file implements `redirectStderr(f *os.File)`. It duplicates the original stderr file descriptor and stores it in `config.PasswordPromptOutput`, then uses `unix.Dup2` to replace stderr with the log file descriptor.

## Control flow
`InitLogging` calls this after opening a non-rotated log file. The function duplicates stderr first for password prompts, then atomically redirects file descriptor 2 to the log file. Failures call `fs.Fatalf`.

## State and persistence behavior
The process file descriptor table is mutated. `config.PasswordPromptOutput` preserves a handle to the original stderr for interactive password prompts. Runtime panic output persists to the log file afterward.

## Dependencies and integration points
It depends on `golang.org/x/sys/unix`, `fs/config`, and core logging fatal helpers. It is selected by build tags for common Unix-like systems except Solaris, Plan 9, and JS.

## Risks and edge cases
Descriptor duplication/redirection failures are fatal. Redirecting stderr is process-wide and affects third-party libraries. Rotating log mode does not use this path, so panic capture differs by log-file configuration.

## Test signals
No direct test exists in this subset. Behavior is typically validated by platform integration tests or manual log-file crash checks.

Source-read signal: reviewed complete local file (26 lines). Functions/methods observed: `redirectStderr`.
