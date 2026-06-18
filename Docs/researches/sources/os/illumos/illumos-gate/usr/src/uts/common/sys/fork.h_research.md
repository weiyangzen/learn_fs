# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fork.h

This header declares extended fork interfaces and flags visible outside strict POSIX/XOPEN profiles.

Interfaces:
- Userland declarations for `forkx(int)`, `forkallx(int)`, and `vforkx(int)`.
- `vforkx()` is annotated as returning twice.

Flags:
- `FORK_NOSIGCHLD` prevents SIGCHLD delivery to the parent when the child terminates, while still allowing job-control stop/continue notifications when requested.
- `FORK_WAITPID` requires reaping by a specific wait on the child PID and blocks wait-for-any or wait-for-process-group reaping. It also prevents automatic reaping from ignored SIGCHLD disposition.

Dependencies and relationships:
- `fork()`, `forkall()`, and `vfork()` are documented as equivalent to the corresponding `*x()` calls with zero flags.
- Definitions are hidden when strict XOPEN/POSIX profile rules exclude extensions.
