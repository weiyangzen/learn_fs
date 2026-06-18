# File Research: sources/os/bsd/dragonflybsd/sys/sys/pioctl.h

procfs ioctl definitions for process stop/event control.

Key responsibilities:
- Defines `struct procfs_status` for process state, flags, event mask, stop reason, and extra value.
- Defines ioctls to set/clear event flags, set/get flags, wait for stop, continue process, and get status.
- Defines stop-event bits for exec, signal, syscall entry/exit, coredump, and exit.
- Defines procfs flags `PF_LINGER` and `PF_ISUGID`.

Important behavior:
- `PF_LINGER` keeps stop state around after the last close of `/proc/<pid>/mem`.
- Event stop flags are used by procfs tracing/debugging control paths.

Dependencies:
- Includes `sys/ioccom.h`.

Notable risks:
- Comments include historical typo-level text, but ioctl values and bit masks are ABI.
- Event-mask semantics overlap with process tracing behavior and must be coordinated with signal/ptrace/procfs code.
