# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/poll.h

## Purpose
Defines the public `poll(2)` file-descriptor event ABI and kernel pollhead notification interface.

## Main Interfaces
- `pollfd_t`: fd, requested events, returned events.
- `nfds_t`: number-of-fds type.
- Public event bits:
  - `POLLIN`, `POLLPRI`, `POLLOUT`
  - `POLLRDNORM`, `POLLWRNORM`, `POLLRDBAND`, `POLLWRBAND`
  - `POLLRDHUP`, `POLLNORM`
  - `POLLERR`, `POLLHUP`, `POLLNVAL`
  - `/dev/poll` controls: `POLLREMOVE`, `POLLONESHOT`, `POLLET`
- Kernel-only flags:
  - `POLLRDDATA`
  - `POLLNOERR`
  - `POLLCLOSED`
- Kernel poll interface:
  - `pollhead_t`
  - `pollwakeup()`
  - `polllock()`
  - `pollunlock()`
  - `pollrelock()`
  - `pollcleanup()`
  - `pollblockexit()`
  - `pollcacheclean()`
  - `pollhead_clean()`
- User prototype:
  - `poll(struct pollfd *, nfds_t, int)`

## Dependencies And Relationships
Kernel and kmem-user paths include `sys/thread.h` and expose pollhead state. `poll_impl.h` contains the private caching implementation.

## Research Notes
`pollhead_t` keeps unused padding for DDI size compatibility; only `ph_list` is semantically used.
