# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_log.c

## Role

Implements kernel logging buffers, `/dev/klog` read/poll/kqueue/async behavior, and the `sendsyslog` syscall path used to forward userland syslog messages to syslogd or the console.

## Key Behavior

- `initmsgbuf()` validates or initializes the persistent kernel message ring and ensures resumed/reused buffers start on a new line.
- `initconsbuf()` allocates a console message buffer.
- `msgbuf_putchar()` and `msgbuf_putchar_locked()` append characters to circular buffers and count dropped bytes when writers overrun readers.
- `logopen()` and `logclose()` enforce single-open `/dev/klog`, initialize kqueue/sigio state, manage the periodic wakeup timeout, and release any registered syslog socket.
- `logread()` blocks or returns `EWOULDBLOCK` when empty, reports dropped bytes, copies ring data to userland, and advances the read pointer.
- `logkqfilter()` and filter callbacks expose readable state through kqueue.
- `logwakeup()` defers wakeups from arbitrary printf contexts by setting a flag without taking locks; `logtick()` periodically performs kqueue, SIGIO, and sleep wakeups.
- `logioctl()` supports `FIONREAD`, async mode, owner/pgrp operations, and privileged `LIOCSFD` registration of the syslogd socket.
- Log stash support stores a bounded queue of userland syslog messages while syslogd is unavailable, tracks drops, and replays messages in order when possible.
- `sys_sendsyslog()` bounds user message length, tries to flush stashed messages, sends the current message, and stashes non-`EFAULT` failures.
- `dosendsyslog()` sends to syslogd’s socket if registered, otherwise honors `LOG_CONS` by stripping priority and writing to console/cnputc fallback.

## Interfaces And Dependencies

Uses `struct msgbuf`, `/dev/klog` device entry points, kqueue, sigio, timeouts, vnode/console output, socket `sosend`, rwlocks, mutexes, `copyin`, `uiomove`, and optional ktrace.

## Notes

`log_mtx` is kept as a leaf lock so kernel printf paths remain usable in many contexts. Actual wakeups are deferred to `logtick()` to avoid taking heavier locks from arbitrary logging call sites.
