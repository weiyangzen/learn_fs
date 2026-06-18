# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/system.c

Minimal fork/exec/wait wrapper for 9nfs helper command execution.

Key responsibilities:
- `system()` forks, execs a named command with argv, and waits for the matching child `Waitmsg`.
- Child exits with the exec error string if `exec()` fails.
- `systeml()` varargs convenience wrapper passes `&name+1` as argv.

Dependencies:
- Plan 9 process APIs: `fork`, `exec`, `wait`, `errstr`, `_exits`.

Notable risks:
- Name collides with standard C `system()` concept but uses Plan 9 `Waitmsg*` semantics.
- `systeml()` relies on varargs layout idiom and caller-supplied nil terminator.
