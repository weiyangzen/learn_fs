# File Research: sources/os/bsd/openbsd-src/sys/sys/socket.h

Public socket ABI: types, options, address families, message headers, ancillary data, sysctl names, and prototypes.

This header defines socket types, creation flags, `SOL_SOCKET` options, linger/splice structures, routing-table constants, address/protocol families, `sockaddr`, `sockaddr_storage`, `sockproto`, shutdown modes, peer credentials, and CTL_NET sysctl name tables. It covers PF_ROUTE, PF_UNIX, PF_LINK, PF_KEY, BPF, and pflow sysctl subtrees.

The send/receive ABI is defined through `struct msghdr`, `struct mmsghdr`, `MSG_*` flags, `struct cmsghdr`, CMSG alignment/navigation macros, and socket-level ancillary types `SCM_RIGHTS` and `SCM_TIMESTAMP`. Userland prototypes cover classic socket calls, batched send/receive, `accept4()`, peer-id lookup, and routing-table selection. Kernel builds get `sstosa()`.

Filesystem/storage relevance: sockets are file descriptors and participate in VFS file operation dispatch, descriptor passing, kqueue, poll/select, and UNIX-domain pathname sockets. `SCM_RIGHTS` also transports file descriptors, including filesystem-backed files.
