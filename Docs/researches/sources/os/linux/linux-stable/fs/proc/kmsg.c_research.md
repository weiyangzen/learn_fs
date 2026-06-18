# File Research: sources/os/linux/linux-stable/fs/proc/kmsg.c

Implements `/proc/kmsg`, exposing the kernel log stream.

Key points:
- `open`, `release`, `read`, and `poll` delegate to `do_syslog()` with `SYSLOG_FROM_PROC`.
- Nonblocking reads return `-EAGAIN` when no unread log data exists.
- Poll waits on `log_wait` and reports readable when unread data exists.
- Registers read-only root entry `kmsg` as permanent.

Dependencies/contracts:
- Uses syslog subsystem semantics and permissions.
- One of the proc entries backed directly by kernel logging infrastructure.
