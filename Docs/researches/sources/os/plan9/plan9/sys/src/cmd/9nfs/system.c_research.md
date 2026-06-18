# File Research: sources/os/plan9/plan9/sys/src/cmd/9nfs/system.c

Minimal Plan 9 process-launch helpers for 9nfs.

Key responsibilities:
- `system(name, argv)` forks, execs a command in the child, and waits for that specific child.
- Child exits with the exec error string if `exec` fails.
- Parent ignores unrelated wait messages until the target pid exits.
- `systeml` provides a varargs wrapper using the argument list after `name`.

Dependencies:
- Uses Plan 9 `fork`, `exec`, `wait`, `Waitmsg`, `errstr`, and `_exits`.

Notable risks:
- `systeml` relies on C varargs layout by taking `&name+1`, matching old Plan 9 style but not portable C.
