# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/socket.h

## Role

Primary public socket API header. It defines socket types, flags, options, address/protocol families, message structures, ancillary-data macros, shutdown constants, and user-visible socket function prototypes.

## Key Contents

Defines `socklen_t`, socket types, `SOCK_CLOEXEC`, `SOCK_NONBLOCK`, `SOCK_NDELAY`, and `SOCK_CLOFORK`. Socket options include traditional bit flags, newer large-number options for attach/detach filters, buffer/time/error/protocol/domain options, credential/timestamp controls, zone/security options, and kernel-only internal options.

Defines socket filter control values, `struct fil_info`, address family constants through `AF_PACKET`, matching `PF_*` aliases, `SOMAXCONN`, `struct msghdr`, compatibility `omsghdr`, 32-bit syscall structures, `MSG_*` flags, `struct cmsghdr`, and `CMSG_*` macros.

## Interfaces

Declares `accept`, `accept4`, `bind`, `connect`, `getpeername`, `getsockname`, `getsockopt`, `listen`, `socketpair`, `recv*`, `send*`, `setsockopt`, `shutdown`, `socket`, and `sockatmark` where namespace rules permit.

## Design Notes

The header contains substantial standards/ABI gating for XPG, POSIX, boot, kernel, and 32-bit syscall views. Several constants are compatibility-bound and must remain synchronized with external consumers such as DTrace IP provider definitions.
