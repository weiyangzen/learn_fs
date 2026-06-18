# File Research: sources/os/linux/linux/fs/proc/kmsg.c

## Scope

This file registers `/proc/kmsg`, a proc interface to the kernel syslog stream.

## Public And Internal APIs Covered

- File callbacks: `kmsg_open()`, `kmsg_release()`, `kmsg_read()`, `kmsg_poll()`.
- Proc ops: `kmsg_proc_ops`.
- Init: `proc_kmsg_init()`.

## Control Flow And Behavior

- Open and release delegate to `do_syslog()` with `SYSLOG_ACTION_OPEN` and `SYSLOG_ACTION_CLOSE` using `SYSLOG_FROM_PROC`.
- Reads return `-EAGAIN` for nonblocking callers when no unread syslog data is available, otherwise delegate to `SYSLOG_ACTION_READ`.
- Poll waits on `log_wait` and reports readable events when `SYSLOG_ACTION_SIZE_UNREAD` is nonzero.
- Init creates permanent `/proc/kmsg` with owner-read mode.

## Dependencies And Risks

- Depends on the kernel syslog implementation and global `log_wait`.
- The proc layer only wraps syslog semantics; authorization and log-consumption policy are enforced in `do_syslog()`.
