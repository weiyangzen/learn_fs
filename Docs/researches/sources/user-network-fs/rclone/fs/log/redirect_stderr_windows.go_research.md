# sources/user-network-fs/rclone/fs/log/redirect_stderr_windows.go

## Purpose
`redirect_stderr_windows.go` implements stderr redirection for Windows by updating the process standard error handle.

## Important APIs, types, and functions
It defines DLL/procedure globals for `kernel32.dll` `SetStdHandle`, helper `setStdHandle`, and `redirectStderr(f *os.File)`.

## Control flow
`redirectStderr` calls `setStdHandle(syscall.STD_ERROR_HANDLE, syscall.Handle(f.Fd()))`. `setStdHandle` invokes the Windows API via `syscall.SyscallN` and translates zero return values into errors. Failures become fatal logging errors.

## State and persistence behavior
The process standard error handle is changed globally, so later stderr writes go to the log file. No other persistent state is maintained by this file.

## Dependencies and integration points
The file depends on Windows syscall APIs and rclone `fs.Fatalf`. It is selected by the `windows` build tag and called by `InitLogging` for non-rotated log files.

## Risks and edge cases
Handle replacement is process-wide and can affect libraries. The code does not preserve the old handle for password prompts like the Unix implementation does. API failures abort process startup.

## Test signals
No direct test is present. Windows build and manual logging/panic capture tests are needed.

Source-read signal: reviewed complete local file (40 lines). Functions/methods observed: `setStdHandle`, `redirectStderr`.
