# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_devctl.c

Read completely: 611 lines.

## Purpose
Implements the `/dev/devctl` kernel event channel used to report device attach, detach, nomatch, and generic notification events to userland.

## Main Elements
- Creates an eternal character device named `devctl` with open, close, read, ioctl, poll, and kqueue filter operations.
- Enforces a single-reader model with `devsoftc.inuse`.
- Maintains a bounded STAILQ event queue backed by a UMA zone, with reserve allocation and oldest-event stealing under memory pressure.
- Registers eventhandlers for `device_attach`, `device_detach`, and `device_nomatch`, converting them into textual devctl records.
- Implements blocking/nonblocking reads, `FIONBIO`, `FIOASYNC`, `FIOSETOWN`, `FIOGETOWN`, poll/select wakeups, kqueue read readiness, and SIGIO notification.
- Exposes tunables/sysctls `hw.bus.devctl_queue` and `hw.bus.devctl_nomatch_enabled`.
- Provides `devctl_notify()` for structured `!system=... subsystem=... type=...` notifications.
- Provides `devctl_safe_quote_sb()` and an optional notify hook through `devctl_set_notify_hook()` / `devctl_unset_notify_hook()`.

## Dependencies And Integration
Integrated with the newbus device tree, eventhandler framework, UMA, character devices, select/poll/kqueue, SIGIO ownership helpers from descriptor code, and optional external notification hooks.

## Risk Notes
Queue disabling destroys the UMA zone and must be serialized with producers. Event loss is possible when queue memory is exhausted. The protocol is string-based, so malformed or overflowing sbuf output is dropped.
