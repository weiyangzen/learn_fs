# File Research: sources/os/bsd/netbsd-src/sys/sys/poll.h

## Purpose
Defines POSIX poll ABI, event flags, kernel common poll routine, and modern `ppoll`/NetBSD `pollts` declarations.

## Main API
- Type: `nfds_t`.
- Structure: `struct pollfd`.
- Event flags: `POLLIN`, `POLLPRI`, `POLLOUT`, `POLLRDNORM`, `POLLWRNORM`, `POLLRDBAND`, `POLLWRBAND`, `POLLERR`, `POLLHUP`, `POLLNVAL`.
- NetBSD timeout constant: `INFTIM`.
- Kernel function: `pollcommon`.
- Userland calls: `poll`, `pollts`, `ppoll`.

## Dependencies
Uses feature-test macros; kernel mode uses signal types, while userland `ppoll`/`pollts` declarations use `sigset_t` and `struct timespec`.

## Risks and Notes
`POLLERR`, `POLLHUP`, and `POLLNVAL` are non-testable returned events. `pollts` is NetBSD-specific and version-renamed for ABI compatibility.
