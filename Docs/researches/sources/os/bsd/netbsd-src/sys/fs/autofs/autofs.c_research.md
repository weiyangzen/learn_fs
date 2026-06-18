# File Research: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs.c

## Summary
Implements AUTOFS control-device operations, automount request queuing, trigger/wait logic, caching, timeouts, and daemon interaction.

## Main Responsibilities
- Define `/dev/autofs` character device open, close, and ioctl handlers.
- Maintain global `autofs_softc` request queue, condition variable, lock, device-open state, daemon session id, and request ids.
- Build trigger paths and keys from autofs nodes.
- Deduplicate concurrent requests for the same path/key.
- Queue requests for automountd and wait for completion.
- Support interruptible waits with temporary signal mask handling.
- Time out pending requests via callout plus workqueue.
- Retry failed triggers according to sysctl-tunable attempts/delay.
- Cache successful nodes and flush caches on update.

## Key Interfaces
- `autofs_trigger()`, `autofs_cached()`, `autofs_flush()`, `autofs_ignore_thread()`, `autofs_timeout_wq()`.
- Ioctls handled: `AUTOFSREQUEST`, `AUTOFSDONE`.

## Risks
This code coordinates kernel VFS threads and userland automountd. Correctness depends on lock ordering between vnode locks, `sc_lock`, and mount locks. Only one daemon can open the device; daemon descendants are identified by process group/session id to avoid self-triggering.
