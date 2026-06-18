# File Research: sources/os/bsd/netbsd-src/sys/sys/event.h

Read completely: 360 lines.

## Purpose
Defines the kqueue/kevent user ABI and kernel knote/filter interfaces for event notification.

## Main Interfaces
- Filters: `EVFILT_READ`, `EVFILT_WRITE`, `EVFILT_VNODE`, `EVFILT_PROC`, `EVFILT_SIGNAL`, `EVFILT_TIMER`, `EVFILT_FS`, `EVFILT_USER`, and others.
- `struct kevent` and `EV_SET`.
- Event actions and flags: `EV_ADD`, `EV_DELETE`, `EV_ENABLE`, `EV_DISABLE`, `EV_ONESHOT`, `EV_CLEAR`, `EV_RECEIPT`, `EV_DISPATCH`, `EV_EOF`, `EV_ERROR`.
- Note flags: vnode notes (`NOTE_DELETE`, `NOTE_WRITE`, `NOTE_EXTEND`, `NOTE_ATTRIB`, `NOTE_RENAME`, `NOTE_REVOKE`, etc.), process notes, timer units, user-event fflag operations.
- Kernel interfaces: `struct filterops`, `struct knote`, `KNOTE`, `knote`, `knote_fdclose`, `klist_*`, `kevent1`, `kfilter_register`, `kfilter_unregister`.
- Userland declarations: `kqueue`, `kqueue1`, `kevent`.

## Dependencies And Integration
Uses feature-test macros, integer types, queue lists, ioctl definitions, file descriptor state, filter registration, and kernel object-specific locks. Vnodes and files attach knotes for notification.

## Risks And Edge Cases
- `struct knote` has explicit field-locking rules across fd-table, kqueue, and object locks.
- `EVFILT_USER` encodes fflag modification operations in high bits.
- `EVFILT_VNODE` depends on vnode code correctly issuing notes for filesystem mutations.
- `EV_ERROR` reports errno in `data`.

## Filesystem Relevance
High. VFS and vnode operations use `EVFILT_VNODE` and `EVFILT_FS` to notify userland of file and mount changes.
