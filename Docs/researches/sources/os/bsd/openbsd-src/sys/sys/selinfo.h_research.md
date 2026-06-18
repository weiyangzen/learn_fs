# File Research: sources/os/bsd/openbsd-src/sys/sys/selinfo.h

Defines selection/poll notification state embedded in kernel objects.

Key contents:
- Includes `<sys/event.h>` for `struct klist`.
- `struct selinfo` containing a kernel note list `si_note`.

Kernel API:
- `selwakeup(struct selinfo *)`.

Integration:
- Used by device, pipe, socket, and other waitable objects to notify select/poll/kqueue waiters.
