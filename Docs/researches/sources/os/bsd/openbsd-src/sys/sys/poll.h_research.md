# File Research: sources/os/bsd/openbsd-src/sys/sys/poll.h

Defines `poll(2)` and `ppoll(2)` public ABI.

Key contents:
- `struct pollfd`/`pollfd_t` and `nfds_t`.
- Event bits: `POLLIN`, `POLLPRI`, `POLLOUT`, `POLLERR`, `POLLHUP`, `POLLNVAL`, normal/band read/write aliases.
- Kernel-only `POLL_NOHUP`.
- `INFTIM`.
- Userland prototypes for `poll` and, under visibility rules, `ppoll`.

Risk notes:
- `ppoll` visibility depends on POSIX 2024 or BSD visibility.
