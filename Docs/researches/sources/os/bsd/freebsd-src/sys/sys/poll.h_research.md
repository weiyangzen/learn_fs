# File Research: sources/os/bsd/freebsd-src/sys/sys/poll.h

This header provides the FreeBSD-compatible `poll.h` ABI. It defines `nfds_t`, `struct pollfd`, requestable event bits, always-reported event bits, BSD extensions, and userland function prototypes.

Requestable events include readable, priority/OOB readable, writable, normal read/write aliases, and band events. BSD-visible extensions add `POLLINIGNEOF` and `POLLRDHUP`. Always-returned events are error, hangup, and invalid descriptor. `POLLSTANDARD` groups the traditional set, and `INFTIM` requests an infinite wait.

For userland, `poll()` is declared. When POSIX.1-2024 visibility is enabled, `sigset_t`, `timespec`, and `ppoll()` are exposed. Fortify support includes `<ssp/poll.h>` when enabled. Filesystem relevance is readiness notification: file descriptors for regular files, pipes, sockets, devices, and filesystem-backed special files report readiness through this ABI.
