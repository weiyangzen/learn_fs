# File Research: sources/virtualization/libguestfs/lib/wait.c

Signal-safe wait wrappers.

Important behavior:
- `guestfs_int_waitpid` retries `waitpid` on `EINTR` and reports other errors with context.
- `guestfs_int_waitpid_noerror` waits while ignoring errors except retrying interruption.
- `guestfs_int_wait4` provides the same retry behavior for `wait4` with rusage collection.
- Comments explain the interaction with non-restartable SIGCHLD handlers installed by embedding programs.

Filesystem relevance:
- Supports robust management of subprocesses used by launch, command helpers, temporary probes, and host-side tooling.
