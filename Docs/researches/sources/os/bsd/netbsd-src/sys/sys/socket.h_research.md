# File Research: sources/os/bsd/netbsd-src/sys/sys/socket.h

Read completely: 661 lines.

This public socket ABI header defines socket types, socket creation flags, socket options, address/protocol family constants, socket address structures, message/control-message layouts, ancillary-data macros, shutdown constants, and libc socket prototypes.

Major types include `struct linger`, `struct accept_filter_arg`, `struct sockaddr`, kernel `struct sockproto` and `sockaddr_big`, `struct sockaddr_storage`, NetBSD `struct sockcred`, `struct kinfo_pcb`, `struct msghdr`, NetBSD `struct mmsghdr`, and `struct cmsghdr`.

It defines AF/PF families through `AF_MAX`, routing sysctl levels, `SOMAXCONN`, message flags, internal-only message flags, CMSG alignment/navigation macros, socket-level control messages, and prototypes for accept/bind/connect/send/receive/socketpair plus NetBSD `sendmmsg`/`recvmmsg`.

Kernel-only declarations add sockaddr allocation, copying, formatting, comparison, and generic address helpers.

Risks: this header is wide ABI surface. Control-message macros depend on alignment constants matching kernel runtime layout, and address-family constants are persistent values used across userland and kernel protocols.
