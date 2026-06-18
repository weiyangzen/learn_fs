# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_log.c

## Summary
Implements the `/dev/klog` character device that exposes the kernel message buffer to syslog-style readers.

## Main Responsibilities
- Provides open, close, read, ioctl, and kqueue filter devops for `klog`.
- Blocks readers until `msgbufp` advances, unless opened nonblocking.
- Supports `FIONREAD`, async I/O ownership, SIGIO delivery, and deprecated tty process-group ioctls.
- Periodically checks `msgbuftrigger` with a callout and wakes readers/kqueue waiters.
- Creates the device at driver SYSINIT.

## Important Behavior
Only one opener is allowed through `log_open`. Reads handle circular message-buffer wrap and may discard old data if the reader falls too far behind. `log_wakeups_per_second` controls callout polling frequency.

## Risks
Message loss is accepted when the log reader lags behind the ring buffer. Wakeups are periodic rather than immediate. Async signaling depends on `sc_sigio` ownership and `LOG_ASYNC`.
