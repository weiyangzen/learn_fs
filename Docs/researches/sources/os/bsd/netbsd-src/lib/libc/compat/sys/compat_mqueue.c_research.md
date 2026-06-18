# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_mqueue.c

Read completely: 86 lines.

This implements old `mq_timedreceive` and `mq_timedsend` with `timespec50` timeouts. Both convert optional timeout pointers to native `timespec` and call the `*50` message-queue wrappers.

Security/reliability notes: no local allocation. The message buffer and priority arguments are forwarded unchanged.
