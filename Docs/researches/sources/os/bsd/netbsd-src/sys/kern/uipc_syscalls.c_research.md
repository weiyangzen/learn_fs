# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_syscalls.c

## Purpose
Implements the NetBSD syscall-facing socket API: socket creation, bind/listen/accept/connect, socketpair, send/receive message paths, socket option access, shutdown, socket name queries, pipe-as-socketpair support, and SCTP peeloff glue.

## Main Interfaces
- `sys___socket30`, `fsocreate` integration: creates socket file descriptors and affixes them to the process descriptor table.
- `sys_bind`, `do_sys_bind`, `sys_listen`, `sys_connect`, `do_sys_connect`: convert user socket addresses and dispatch to socket/protocol operations.
- `do_sys_accept`, `sys_accept`, `sys_paccept`: allocate a new descriptor, dequeue a pending connection, inherit/adjust flags, support signal-mask accept.
- `sys_socketpair`: creates and connects two sockets, including datagram symmetry handling.
- `sys_sendto`, `sys_sendmsg`, `do_sys_sendmsg`, `do_sys_sendmsg_so`: build `uio`/mbuf arguments, validate iov lengths, call protocol send operation.
- `sys_recvfrom`, `sys_recvmsg`, `do_sys_recvmsg`, `do_sys_recvmsg_so`, `sys_sendmmsg`, `sys_recvmmsg`: receive/send batched messages, copy names/control data, handle partial progress.
- `copyout_msg_control`, `free_control_mbuf`, `free_rights`: externalize control mbufs, including cleanup for truncated `SCM_RIGHTS`.
- `sys_setsockopt`, `sys_getsockopt`, `sys_getsockopt2`: copy socket option payloads and synchronize `SO_NOSIGPIPE` with file flags.
- `pipe1` under `PIPE_SOCKETPAIR`: implements pipes as connected AF_LOCAL stream sockets.
- `do_sys_getsockname`, `do_sys_getpeername`, `copyout_sockname*`, `sockargs*`: address conversion helpers.
- `do_sys_peeloff`: optional SCTP association peeloff into a new socket descriptor.

## State And Control Flow
The file bridges user ABI structures to kernel socket/protocol calls. It obtains descriptor references with `fd_getsock`/`fd_getsock1`, allocates descriptors with `fd_allocfile`, and releases or aborts them carefully on copyout or protocol failures. Send/receive convert user iovecs to `uio`, enforce `IOV_MAX` and `SSIZE_MAX`, convert destination/control data into mbufs, and use ktrace hooks around user-visible data. Accept/connect paths hold socket locks around queue and state transitions, with special handling for nonblocking connect, interrupted connect, and paccept signal-mask setup.

## Dependencies And Integration
Depends on socket core (`struct socket`, `soaccept`, `soconnect`, `soshutdown`, `so_send`, `so_receive`), descriptor table management, mbuf allocation, ktrace, signal delivery, kqueue/select side effects through socket buffers, SCTP optional code, and AF_LOCAL helpers for pipe socketpairs.

## Risks And Edge Cases
- Descriptor lifetime is delicate in accept/socketpair/peeloff: failures must close or abort exactly the descriptors already allocated.
- Partial send/receive deliberately suppresses `EINTR`, `ERESTART`, and `EWOULDBLOCK` after bytes are transferred.
- `copyout_msg_control` must close newly externalized descriptors if user control-buffer copyout truncates or fails.
- `sockargs` enforces address/control length limits and retains 4.3BSD address-family compatibility behavior.
- `recvmmsg` defers post-success errors in `so->so_rerror`, so next receive can surface them.

## Filesystem Relevance
Indirect but important. This is descriptor/syscall substrate rather than VFS code, but Unix-domain sockets, pipes, `SCM_RIGHTS`, and descriptor lifecycle interact with filesystem objects and vnode-backed descriptors.
