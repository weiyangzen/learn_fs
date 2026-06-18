# sources/sync-backup/rsync/cmd-or-msg

## Purpose
Small shell helper that runs a command and, on failure, tells the user which configure option can disable the failing feature. It is used as user-facing build/configuration glue rather than runtime rsync logic.

## Important APIs, Types, and Functions
The script takes an option name as `$1`, shifts it off, echoes the command to be executed, runs the remaining arguments as a command via `"${@}"`, and prints `re-run .../configure with --$opt` before exiting 1 if the command fails.

## Control Flow
It derives `srcdir` from `$0`, captures `opt`, shifts, echoes the exact command arguments, executes them, and only enters the diagnostic branch on non-zero exit.

## State and Persistence Behavior
No persistent state is written. Effects are limited to stdout/stderr messages and the wrapped command's side effects.

## Dependencies and Integration Points
Depends on POSIX `/bin/sh`, `dirname`, and the caller passing a valid command. It integrates with configure/build checks that want a consistent fallback message for optional generated artifacts or feature probes.

## Risks and Test Signals
Risks are mostly shell portability and argument handling: an empty command will fail unclearly, and the option text is trusted. Test signals are that a successful wrapped command returns 0 with only the echo, while a failing wrapped command returns 1 and names the expected `configure --<option>` remediation.
