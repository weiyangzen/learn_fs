# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat___msgctl13.c

Read completely: 68 lines.

This implements old `__msgctl13` for SysV message queues. For `IPC_SET`, it converts `msqid_ds13` to native, calls `__msgctl50`, and for `IPC_STAT` converts native results back to `msqid_ds13`.

Important interactions: relies on conversion helpers from `compat/sys/msg.h`.

Security/reliability notes: `ds13` must be valid for commands that need it. Field truncation is part of old ABI conversion.
