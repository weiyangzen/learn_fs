# File Research: sources/os/bsd/freebsd-src/sys/sys/event.h

## Purpose
Defines the kqueue/kevent public ABI and kernel-side knote/filter interfaces.

## Main Interfaces
- Public filters: `EVFILT_READ`, `WRITE`, `AIO`, `VNODE`, `PROC`, `SIGNAL`, `TIMER`, `PROCDESC`, `FS`, `LIO`, `USER`, `SENDFILE`, `EMPTY`, `JAIL`, `JAILDESC`.
- `EV_SET` initializer, with C99 compound-literal and older fallback forms.
- `struct kevent`, compatibility `freebsd11_kevent`, and 32-bit ABI structures.
- Event action/result flags: `EV_ADD`, `EV_DELETE`, `EV_ENABLE`, `EV_DISABLE`, `EV_ONESHOT`, `EV_CLEAR`, `EV_RECEIPT`, `EV_DISPATCH`, `EV_EOF`, `EV_ERROR`.
- Filter flags: `NOTE_*` for user, file, vnode, process, jail, and timer filters.
- Kqueue flags: `KQUEUE_CLOEXEC`, `KQUEUE_CPONFORK`.
- Kernel structures:
  - `struct knlist`
  - `struct filterops`
  - `struct knote`
  - `struct kevent_copyops`
- Kernel APIs for knote list management, filter registration, fd close notification, and kqueue task draining.
- Userland syscalls: `kqueue`, `kqueuex`, `kqueue1`, `kevent`.

## Dependencies And Integration
Includes queue primitives and ABI types. Kernel knotes integrate with files, vnodes, processes, jails, AIO, kqueues, and polling/select notification paths.

## Risk Notes
`struct kevent` layout is user ABI. Kernel `knote` locking rules are subtle: kqueue lock, knlist lock, and `kn_influx`/`KN_SCAN` state coordinate concurrent detach and scan paths.
