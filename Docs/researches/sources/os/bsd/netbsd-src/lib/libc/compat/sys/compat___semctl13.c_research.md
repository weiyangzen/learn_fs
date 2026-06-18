# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___semctl13.c

Read completely: 108 lines.

This implements old varargs `__semctl13`. It extracts `union __semun` for commands that require an argument, converts `semid_ds13` to native for `IPC_SET`, points the union at a native temporary, calls `____semctl50`, and converts native output back for `IPC_STAT`.

Important interactions: handles the awkward SysV `semctl` varargs ABI and old structure layout.

Security/reliability notes: correctness depends on callers passing the expected vararg for commands that require it. The lint-only path uses `memcpy` to quiet varargs diagnostics.
