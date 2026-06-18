# File Research: sources/os/bsd/openbsd-src/sys/sys/event.h

This header defines the kqueue/kevent userspace ABI and kernel knote/filter interface.

Key definitions:
- Filters: `EVFILT_READ`, `WRITE`, `AIO`, `VNODE`, `PROC`, `SIGNAL`, `TIMER`, `DEVICE`, `EXCEPT`, `USER`.
- `struct kevent` and `EV_SET`.
- Event action/flag constants: `EV_ADD`, `EV_DELETE`, `EV_ENABLE`, `EV_DISABLE`, `EV_ONESHOT`, `EV_CLEAR`, `EV_RECEIPT`, `EV_DISPATCH`, `EV_EOF`, `EV_ERROR`.
- Filter notes for read/write/except, vnode, proc, device, timer, and user events.
- Public `struct klist` and `SLIST_HEAD(knlist, knote)` compatibility exposure.

Kernel definitions:
- Internal flags such as `__EV_SELECT`, `__EV_POLL`, `__EV_HUP`, `NOTE_SUBMIT`, `NOTE_SIGNAL`.
- `struct filterops`, `struct knote`, `struct klistops`, `struct kqueue_scan_state`.
- APIs for knote/kqueue registration, scan, poll, list operations, and inline helpers `knote_modify`, `knote_process`, `klist_empty`.

Userland declarations:
- `kqueue`
- `kqueue1`
- `kevent`

Risk notes:
- `struct kevent` is syscall ABI and must remain stable.
- Kernel filterops concurrency rules are documented in the header; filter implementations depend on serialized attach/detach/modify/process callbacks.
