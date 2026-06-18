# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_log.c

## Purpose
Implements the `/dev/klog` character device, exposing the kernel message buffer to user space log readers such as syslog daemons.

## Main Interfaces
- Device operations: `logopen`, `logclose`, `logread`, `logioctl`, `logpoll`, `logkqfilter`.
- `logtimeout()`: periodic wakeup path for select/poll/kqueue/async readers.
- `log_drvinit()`: initializes condition variable, callout, knote list, and creates the `klog` device.

## Implementation Notes
Only one reader may open the device at a time, guarded by `msgbuf_lock` and `log_open`. On open, a callout is scheduled at `kern.log_wakeups_per_second`; invalid values below one are corrected. Reads block on `log_wakeup` unless `IO_NDELAY` is set, then copy from `msgbufp` using `msgbuf_getbytes()` in 128-byte chunks.

Polling and kqueue readiness are based on `msgbuf_getcount(msgbufp)`. `logtimeout()` checks `msgbuftrigger`; if set, it clears the trigger and wakes selectors, knotes, SIGIO subscribers, and condition-variable waiters, then reschedules itself.

`logioctl()` supports `FIONREAD`, async mode, owner get/set, and deprecated tty process-group aliases.

## Dependencies
Uses `msgbuf_lock`, `msgbufp`, `msgbuftrigger`, condition variables, callouts, select/poll/kqueue, sigio ownership, and FreeBSD character device registration.

## Research Notes
The design decouples writers from sleeping log readers: writers set `msgbuftrigger`, while the callout performs wakeups. This keeps kernel logging usable from sensitive contexts.
