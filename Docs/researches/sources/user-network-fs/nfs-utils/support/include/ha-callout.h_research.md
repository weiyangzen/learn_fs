# sources/user-network-fs/nfs-utils/support/include/ha-callout.h

## Purpose
Implements inline high-availability callout execution for mountd/statd event hooks.

## Important APIs, Types, and Functions
Defines global `ha_callout_prog` and inline `ha_callout(event,arg1,arg2,arg3)`, which forks and execs the configured script.

## Control Flow
If no program is configured the call returns. Otherwise it formats `arg3`, temporarily restores default `SIGCHLD`, forks, execs the script with event arguments, waits, restores the signal action, and logs the exit status.

## State and Persistence Behavior
No persistent state beyond external script effects. It temporarily mutates process `SIGCHLD` handling and waits for one child.

## Dependencies and Integration Points
Depends on fork/exec/wait/sigaction and `xlog`. Integrated by daemons that support HA event scripts.

## Risks and Edge Cases
Inline code in a header pulls process-control behavior into all users. `WEXITSTATUS` is used without checking normal exit. Script path and arguments are trusted process configuration.

## Test Signals
Test disabled mode, fork/exec failure, negative and nonnegative arg3, SIGCHLD restoration, and script exit logging.
