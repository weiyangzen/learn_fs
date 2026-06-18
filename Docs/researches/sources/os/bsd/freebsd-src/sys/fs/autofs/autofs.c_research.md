# File Research: sources/os/bsd/freebsd-src/sys/fs/autofs/autofs.c

## Purpose
Core kernel implementation for FreeBSD autofs device state, request queue, trigger coordination, caching, tunables, and daemon ioctls.

## Main Elements
- Defines `M_AUTOFS`, UMA zones for requests and nodes, `/dev/autofs` cdev operations, and global `autofs_softc`.
- Sysctls/tunables control debug output, mount-on-stat behavior, daemon timeout, cache lifetime, retry attempts/delay, and signal interruptibility.
- `autofs_init()` allocates softc, initializes queues/locks/cv/zones, and creates `/dev/autofs`.
- `autofs_uninit()` refuses unload while the device is open and destroys device/zones/softc.
- `autofs_ignore_thread()` prevents automountd and descendants from recursively triggering autofs, using the session ID of the daemon that opened the device.
- `autofs_trigger_one()` creates or joins a request, starts timeout task, waits for daemon completion, handles signals, applies positive caching, and cleans up refcounted request state.
- `autofs_trigger()` retries failed triggers according to tunables except for signal interruption.
- `autofs_ioctl_request()` gives automountd the next pending request and records daemon session ID.
- `autofs_ioctl_done_101()` and `autofs_ioctl_done()` complete requests and wake blocked threads.
- Timeout task completes stuck requests with `ETIMEDOUT`.

## Dependencies And Integration
Integrates with FreeBSD VFS, cdev, taskqueue, callout, UMA, sysctl, signal mask, and automountd ioctl protocol.

## Risk Notes
Correctness depends on `sc_lock`, request refcounts, timeout cancellation/draining, and avoiding daemon self-trigger recursion.
