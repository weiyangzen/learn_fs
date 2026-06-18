# File Research: sources/os/linux/linux/fs/ocfs2/cluster/masklog.c

Runtime-configurable logging mask implementation for OCFS2/O2CB cluster code.

State:
- `mlog_and_bits`: masks explicitly allowed, initialized to errors and notices.
- `mlog_not_bits`: masks explicitly denied.
- Both are exported GPL symbols.

Logging:
- `__mlog_printk()` checks allow/deny masks, selects kernel log level, prefixes errors, and prints task name, pid, CPU, function, line, and formatted message.

Sysfs:
- Creates one attribute per mask bit under the O2CB logmask kset.
- Each attribute supports `allow`, `deny`, and `off`.
- `mlog_sys_init()` attaches the `logmask` kset under the O2CB kset.
- `mlog_sys_shutdown()` unregisters it.

Mask attributes:
- Covers TCP, MSG, SOCKET, HEARTBEAT, HB_BIO, DLMFS, DLM, DLM_DOMAIN, DLM_THREAD, DLM_MASTER, DLM_RECOVERY, DLM_GLUE, VOTE, CONN, QUORUM, BASTS, CLUSTER, ERROR, NOTICE, and KTHREAD.

Concurrency:
- Updates to global mask words are plain bit operations without explicit locking; this logging path favors low overhead.
