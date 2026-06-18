# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_semctl.c

Read completely: 100 lines.

This implements old public `semctl` for `semid_ds14`. It extracts varargs for commands that use `union __semun`, converts old structures to native for `IPC_SET`, calls `__semctl50`, and converts back for `IPC_STAT`.

Security/reliability notes: varargs ABI misuse by callers is not locally detectable. Structure conversion carries historical field-width limits.
