# File Research: sources/os/bsd/dragonflybsd/sys/kern/uipc_syscalls.c

## Role

This file implements the system-call front end for socket operations and `sendfile(2)`. It marshals user arguments into kernel objects, allocates file descriptors, copies socket addresses, iovecs, message headers, ancillary data, and option buffers, applies jail address filtering, calls generic socket routines, and copies results back to user space.

It is the boundary layer between user ABI structures and the internal socket API in `uipc_socket.c`.

## Socket Creation And Binding

`kern_socket()` handles `SOCK_NONBLOCK`, `SOCK_CLOEXEC`, and `SOCK_CLOFORK` flags embedded in the socket type, allocates a file descriptor/file object, creates a socket with `socreate()`, initializes `socketops`, sets descriptor close flags, publishes the file descriptor, and drops the allocation reference.

`sys_socket()` is the syscall wrapper around `kern_socket()`.

`kern_bind()` holds the socket file, calls `sobind()`, and drops the file reference.

`sys_bind()` copies in the sockaddr with `getsockaddr()`, checks jail remote-address policy through `prison_remote_ip()`, calls `kern_bind()`, and frees the sockaddr.

`kern_listen()` and `sys_listen()` hold the socket and call `solisten()`.

## Accept

`soaccept_predicate()` is the readiness predicate for accept. It checks listener errors, removes a completed child from `so_comp` under the listener pool token, references it, clears `so_head`, handles closed listeners and nonblocking mode, and returns whether the wait condition is satisfied.

`kern_accept()` allocates the new descriptor before waiting, validates that the listener has `SO_ACCEPTCONN`, derives accepted file flags from the listener plus optional `extaccept`/`accept4` behavior, tries a fast predicate path when enabled, otherwise blocks via `netmsg_so_notify`, initializes the new file, inherits async ownership unless `SOCK_KERN_NOINHERIT` is set, calls `soaccept()` or uses cached `so_faddr`, copies out the peer address when requested, and publishes or clears the reserved descriptor.

`sys_accept()`, `sys_extaccept()`, and `sys_accept4()` copy address-length inputs, call `kern_accept()`, apply `prison_local_ip()` before copying out peer addresses, copy out final address lengths, and free allocated sockaddr storage. `accept4()` validates only `SOCK_NONBLOCK`, `SOCK_CLOEXEC`, and `SOCK_CLOFORK`.

## Connect

`soconnected_predicate()` completes when a socket is no longer connecting or has an error.

`kern_connect()` holds the socket, derives blocking flags, rejects a second connection already in progress, calls `soconnect()`, returns `EINPROGRESS` for nonblocking connects still in progress, otherwise waits via `netmsg_so_notify` until connection completion or error. It consumes `so_error` and maps restart to interrupt as needed.

`sys_connect()` and `sys_extconnect()` copy in and jail-check destination sockaddrs, call `kern_connect()` with default or extended flags, then free the sockaddr.

## Socketpair

`kern_socketpair()` handles type flags, creates two sockets, allocates two descriptors, connects them through `soconnect2()`, does a second reverse connect for datagram sockets because datagram socketpair linkage is asymmetric, initializes both file objects and descriptor flags, and publishes both descriptors. Failure paths close sockets and clear descriptors in reverse order.

`sys_socketpair()` copies out the descriptor pair and closes both descriptors if copyout fails.

## Send And Receive Message Syscalls

`kern_sendmsg()` holds the socket, optionally captures ktrace I/O metadata, derives nonblocking message flags from file flags, calls protocol `so_pru_sosend()`, suppresses interrupt/would-block errors after a partial send, raises SIGPIPE on `EPIPE` unless disabled by flags or socket option, returns byte count, and drops the file reference.

`sys_sendto()` builds a one-element write `uio`, optionally copies and jail-checks the destination sockaddr, calls `kern_sendmsg()`, and frees the sockaddr.

`sys_sendmsg()` copies in `struct msghdr`, conditionally copies in destination sockaddr, copies in iovecs with `iovec_copyin()`, copies in a single control mbuf when present, validates control length against `sizeof(struct cmsghdr)` and `MLEN`, calls `kern_sendmsg()`, and frees iovec/sockaddr resources. Control ownership passes to the send path on success or failure from `kern_sendmsg()`.

`kern_recvmsg()` mirrors send: it holds the socket, captures optional ktrace metadata, derives nonblocking flags from file flags, calls protocol `so_pru_soreceive()`, suppresses interrupt/would-block errors after partial receive, returns byte count, and drops the file reference.

`sys_recvfrom()` builds a one-element read `uio`, copies in the source-address buffer length, calls `kern_recvmsg()`, applies `prison_local_ip()` to returned sockaddr, copies out address and length, and frees the sockaddr.

`sys_recvmsg()` copies in `struct msghdr`, validates name/control lengths, copies iovecs, calls `kern_recvmsg()` with optional sockaddr/control returns, copies out source address, copies out control mbuf data with `MSG_CTRUNC` if the user buffer is too small, writes final control length and message flags, then frees sockaddr, iovec, and control mbufs.

## Socket Options And Names

`kern_setsockopt()` validates `sockopt` pointer/size combinations, holds the socket, and calls `sosetopt()`.

`sys_setsockopt()` copies user option data into a kernel temporary buffer when present, caps size to `SOMAXOPT_SIZE`, calls `kern_setsockopt()`, and frees the temporary buffer.

`kern_getsockopt()` validates `sockopt`, holds the socket, and calls `sogetopt()`.

`sys_getsockopt()` copies in the requested size, permits root to request up to `SOMAXOPT_SIZE0` with nullable allocation, copies the user's existing option buffer into kernel memory when present, calls `kern_getsockopt()`, then copies out final size and option bytes.

`kern_getsockname()` and `kern_getpeername()` hold the socket, validate input length, call protocol address methods, truncate returned lengths to user capacity, and return allocated sockaddr storage. `kern_getpeername()` requires connected or confirming state.

`sys_getsockname()` copies out the bound local address. For unnamed AF_LOCAL sockets where the protocol returns no sockaddr, it synthesizes an `AF_LOCAL` sockaddr with the requested/truncated length.

`sys_getpeername()` copies out the peer address and final length after applying jail local-address translation.

`getsockaddr()` validates sockaddr length against `SOCK_MAXADDRLEN` and minimum sockaddr header size, allocates `M_SONAME`, copies in the user buffer, and stores the actual length into `sa_len`.

## Sendfile

`sys_sendfile()` validates the input file as a vnode, references the vnode, copies optional `sf_hdtr`, converts headers into an mbuf chain with `m_uiomove()`, calls `kern_sendfile()`, then sends trailers through `kern_sendmsg()` as a writev fallback. It returns total file plus trailer bytes through `sbytes` when requested.

`kern_sendfile()` validates a regular-file vnode with VM object, holds the output socket, requires a connected stream socket, rejects negative offsets, and requires `SSB_PREALLOC` or `SSB_STOPSUPP` support to prevent unlimited mbuf buildup during async sends.

The sendfile loop:

- Locks the send buffer and holds the VM object shared.
- Calculates page-sized transfer chunks bounded by EOF and requested byte count.
- Checks socket space early for nonblocking sockets.
- Looks up a VM page with `vm_page_lookup_sbusy_try()`.
- If missing, performs `VOP_READ_FP()` with `UIO_NOCOPY` to populate VM pages, then retries.
- Allocates an `sf_buf`, wraps it in an external-storage mbuf whose free callback is `sf_buf_mfree()`.
- Prepends any header mbuf chain to the first data mbuf.
- Waits for socket space, rechecking `SS_CANTSENDMORE` and `so_error` after any blocking work.
- Preallocates stream accounting when needed.
- Dispatches through async `so_pru_senda()` or synchronous `so_pru_send()`.

`sf_buf_mfree()` releases the sendfile buffer and drops the page soft-busy reference when the external mbuf storage is freed.

## Notable Assumptions And Risks

- Syscall wrappers carefully separate descriptor allocation/publication from socket creation to avoid leaking partially initialized descriptors.
- The accept path relies on pool-token protection because queued sockets may have zero ordinary references until accepted.
- `sys_sendmsg()` supports only a control payload that fits in one mbuf (`MLEN`) at this boundary.
- `sys_getsockopt()` copies the user's existing option buffer into kernel memory before `sogetopt()`, matching the internal `sockopt` convention used here.
- `sendfile()` depends on VM object/page lifetime, socket-buffer preallocation/stop support, and external mbuf callbacks; error paths must release vnode, VM object, socket lock, file refs, and header mbufs in the correct order.
