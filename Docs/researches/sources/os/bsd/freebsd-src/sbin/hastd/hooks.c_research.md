# File Research: sources/os/bsd/freebsd-src/sbin/hastd/hooks.c

Read completely: 389 lines.

This file manages asynchronous external hook execution for HAST events. It forks configured executables, tracks child PIDs and command strings, reports long-running hooks, and logs hook termination status.

Key responsibilities:
- Initializes and destroys a global `hookprocs` queue protected by a mutex.
- Builds a bounded printable command string from hook path and arguments.
- Forks hook children with almost all descriptors closed and stdio redirected to `/dev/null` when logging to syslog.
- Restores an empty signal mask in hook children before `execv()`.
- Tracks hook PID, birth time, and last report time.
- Reaps known hook children through `hook_check_one()` and warns about missing or long-running hook processes through `hook_check()`.

Important interactions:
- Called by the daemon main loop after SIGCHLD and at periodic intervals.
- Uses `pjdlog` for status/error reporting and local synchronization wrappers from `synch.h`.
- Hook command construction uses `snprlcat()` from `subr.h`.

Reliability and security notes:
- Hooks run as forked external programs and inherit only intentionally preserved descriptors.
- Argument collection is capped at 64 entries and asserts that the varargs list terminates.
- Long command strings are rejected if they fill `PATH_MAX`.
- `hook_fini()` frees tracked hook records but does not kill running hooks; shutdown policy is handled elsewhere.
