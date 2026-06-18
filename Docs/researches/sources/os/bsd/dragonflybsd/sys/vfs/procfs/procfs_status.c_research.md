# File Research: sources/os/bsd/dragonflybsd/sys/vfs/procfs/procfs_status.c

This file implements `/proc/<pid>/status` and `/proc/<pid>/cmdline`. `procfs_dostatus()` accepts reads only and formats process name, pid/ppid/pgrp/session, controlling terminal, session flags, start/user/system CPU times, wait channel, uid/gid/groups, and jail hostname.

`procfs_docmdline()` emits command-line text. It prefers writable thread/process title mappings when allowed, then cached process args when allowed, then `p_comm` for other processes, and for the current process can fall back to reading `PS_STRINGS` and argv pointers from user space. Access to full args is gated by `ps_argsopen` or normal debug permissions.

Research notes: `procfs_dostatus()` uses a fixed 256-byte buffer with explicit overflow checks. `procfs_docmdline()` intentionally returns zero-length in some unavailable-argv cases to match Linux-like behavior.
