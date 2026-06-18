# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/unix.c

Read status: complete, 592 lines.

This is the Unix portability backend for Plan 9 `rc`. It supplies platform-specific implementations for environment import/export, command execution, signals, directory scanning, file descriptor wrappers, allocation, and wait-status handling.

Important entry points include `Vinit`, `execfinit`/`Xrdfn`, `mkenv`, `Waitfor`, `Execute`, `Opendir`/`Readdir`/`Closedir`, `Trapinit`, `execumask`, and the small wrappers around `read`, `write`, `lseek`, `dup`, `creat`, `unlink`, `malloc`, and `fork`.

Environment handling encodes multiword `rc` variables using separator byte `'\1'`, exports functions as Bourne-compatible-looking `#()fn ...` environment strings, and sorts exported variables for deterministic `execve` environments. `Execute` searches a supplied path list, retries `ETXTBSY`, and falls back to `/bin/sh` on `ENOEXEC`.

Signal logic maps Unix signals to `rc` trap names and wait statuses. `rfork` is reduced to `fork`, and waitpid tracking is implemented with a small dynamic integer list.

Filesystem relevance: this file adapts Plan 9 shell behavior to Unix directory and file descriptor APIs, especially `/dev/fd` naming, directory glob support, and environment-backed process execution.
