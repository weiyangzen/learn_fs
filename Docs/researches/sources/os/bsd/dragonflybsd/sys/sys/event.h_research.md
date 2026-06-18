# File Research: sources/os/bsd/dragonflybsd/sys/sys/event.h

`event.h` defines DragonFly's kqueue/kevent public ABI and kernel knote infrastructure. Public content includes `EVFILT_*` filter IDs, `EV_SET()`, `struct kevent`, event action flags, returned flags, and `NOTE_*` filter-specific hint bits for user, read/write, exception, vnode, and process events.

For kernel or structure-visible builds, it defines `struct kqinfo`; for `_KERNEL`, it defines `KNOTE`, internal note flags, `filterops`, `struct knote`, scan/timeout flags, copyin/copyout callback types, and prototypes for kqueue/knote operations.

For userland or virtual-kernel builds, it declares `kqueue()` and `kevent()`. This header is both a syscall ABI definition and the central kernel event-notification contract.
