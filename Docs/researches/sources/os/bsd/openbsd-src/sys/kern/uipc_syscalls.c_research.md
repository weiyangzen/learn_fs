# File Research: sources/os/bsd/openbsd-src/sys/kern/uipc_syscalls.c

Socket-related system call glue.

This file maps user-visible socket syscalls to the generic socket core. `sys_socket()` validates type flags, applies pledge restrictions, creates a socket, allocates a file descriptor, installs `socketops`, applies close-on-exec/close-on-fork/nonblocking flags, and tags DNS-restricted sockets. `sys_bind()`, `sys_listen()`, `sys_connect()`, `sys_accept()`, and `sys_accept4()` convert user arguments to mbufs or descriptors, enforce special YP/DNS restrictions, lock sockets, call the corresponding core operation, and handle blocking connection/accept waits.

`doaccept()` allocates the result file before removing an accepted child from the listen queue, honors `accept4()` flags or inherited nonblocking mode, calls `soaccept()`, copies the peer address out, then installs the descriptor. `sys_socketpair()` creates two sockets, connects them with `soconnect2()`, performs a second connect for datagram symmetry, allocates two descriptors, and rolls back carefully on partial failure.

The send side is implemented by `sys_sendto()`, `sys_sendmsg()`, `sys_sendmmsg()`, and `sendit()`. These paths copy in message headers and iovecs, cap batch sends to 1024 datagrams, validate iovec totals against `SSIZE_MAX`, convert destination addresses and control data with `sockargs()`, enforce DNS port 53 for DNS-restricted sockets, invoke `sosend()`, translate partial interrupt/would-block cases to success, optionally send `SIGPIPE`, update file transfer counters, and emit KTRACE records.

The receive side is implemented by `sys_recvfrom()`, `sys_recvmsg()`, `sys_recvmmsg()`, and `recvit()`. These copy in iovecs, support `MSG_WAITFORONE` and timeout-limited receive batches, call `soreceive()`, copy out peer addresses and ancillary data with truncation handling, preserve returned message flags, update file read counters, and defer stored errors after partial `recvmmsg()` success by writing them back into `so_error`.

Socket option and name syscalls allocate option mbufs, enforce maximum option size, call `sosetopt()`/`sogetopt()`, and copy results. `sys_getsockname()` and `sys_getpeername()` obtain protocol addresses with `pru_sockaddr()`/`pru_peeraddr()` and use `copyaddrout()` for userspace truncation semantics. `sockargs()` centralizes sockaddr/control mbuf construction, length validation, cluster allocation, copying, and `sa_len` repair; `getsock()` validates descriptor type.

The tail implements routing-table selection syscalls and legacy YP support. `sys_setrtable()` validates privileges and table existence before changing the process routing table. `sys_ypconnect()` reads `/var/yp/binding/<domain>.2`, validates the binding file and lock, rejects unsafe ports, creates an AF_INET socket, connects using reserved-port semantics for root, marks the socket `SS_YP`, and installs a close-on-exec nonblocking descriptor.

Notable constraints: `SOCK_DNS` is only valid for AF_INET/AF_INET6 and restricts destinations to port 53; address lengths are limited by `sa_len`'s `UCHAR_MAX`; control mbufs are limited to `MCLBYTES`; and syscall wrappers are responsible for all userspace copy, pledge, KTRACE, fd-table, and rollback behavior around the core socket routines.
