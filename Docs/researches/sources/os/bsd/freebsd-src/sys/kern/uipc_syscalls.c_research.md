# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_syscalls.c

This file is the FreeBSD system-call glue for sockets. It translates user arguments and file descriptors into kernel socket operations, performs capability/MAC/audit/ktrace checks, allocates and initializes `struct file` descriptors, copies socket addresses/control data to and from userspace, and preserves legacy 4.3BSD compatibility behavior where enabled.

Key entry points:
- `getsock_cap()` and `getsock()` convert a file descriptor into a referenced socket `struct file`, enforcing required capability rights and rejecting non-socket descriptors.
- `sys_socket()` and `kern_socket()` implement `socket(2)`, including `SOCK_CLOEXEC`, `SOCK_CLOFORK`, and `SOCK_NONBLOCK` flag extraction, descriptor allocation, `socreate()`, `finit()`, and nonblocking synchronization through `FIONBIO`.
- `sys_bind()`, `sys_bindat()`, and `kern_bindat()` copy in socket addresses, enforce capability-mode path restrictions for `AT_FDCWD`, audit/trace addresses, apply MAC checks, and call `sobind()` or `sobindat()`.
- `sys_listen()` and `kern_listen()` fetch the socket, perform MAC checks, and call `solisten()`.
- `accept1()`, `sys_accept()`, `sys_accept4()`, `kern_accept()`, and `kern_accept4()` implement accept, accept4 flags, descriptor allocation for accepted sockets, capability inheritance, listener queue dequeue, file flag inheritance/override, `soaccept()`, and user sockaddr copyout.
- `sys_connect()`, `sys_connectat()`, and `kern_connectat()` copy in destination addresses, enforce capability-mode restrictions, apply MAC and ktrace hooks, call `soconnectat()`, and wait for blocking connects to complete.
- `sys_socketpair()` and `kern_socketpair()` create two sockets and two file descriptors, connect them with `soconnect2()`, handle asymmetric datagram setup, copy UNIX peer credentials for connected local sockets, and roll back partially-created descriptors/sockets on failure.
- `sendit()`, `kern_sendit()`, `sys_sendto()`, `sys_sendmsg()`, and legacy `osend()` / `osendmsg()` implement send-side syscall argument conversion, control mbuf creation, capability-right choice, MAC checks, `uio` construction, `sousrsend()`, and ktrace I/O logging.
- `kern_recvit()`, `recvit()`, `kern_recvfrom()`, `sys_recvfrom()`, `sys_recvmsg()`, and legacy receive wrappers implement receive-side syscall conversion, `uio` construction, `soreceive()`, address/control copyout, truncation flags, returned byte counts, and ktrace logging.
- `sys_shutdown()` and `kern_shutdown()` validate shutdown mode, call `soshutdown()`, and preserve old ABI behavior that mapped `ENOTCONN` to success for older processes.
- `sys_setsockopt()`, `kern_setsockopt()`, `sys_getsockopt()`, and `kern_getsockopt()` build `struct sockopt`, distinguish user vs kernel option buffers, enforce capability rights, and call `sosetopt()` / `sogetopt()`.
- `sys_getsockname()`, `sys_getpeername()`, compatibility variants, `kern_getsockname()`, `kern_getpeername()`, `user_getsockname()`, and `user_getpeername()` obtain local/peer addresses and copy bounded results to userspace.
- `sockargs()`, `getsockaddr()`, and `m_dispose_extcontrolm()` provide shared sockaddr/control mbuf copyin and externalized `SCM_RIGHTS` cleanup.

Core mechanics:
- All syscall paths begin by converting user descriptors into referenced `struct file` objects and end by `fdrop()`-ing them. Error paths explicitly close newly allocated descriptors with `fdclose()` where a partially-initialized descriptor was published.
- Capability rights are operation-specific: bind/listen/accept/connect/send/receive/shutdown/getopt/setopt/name queries each use separate `cap_*_rights`. Sending to an explicit destination requires combined send/connect rights.
- MAC hooks are placed before operations that create, bind, listen, accept, connect, send, or receive on sockets. Address-based checks use the copied-in `struct sockaddr`.
- Audit hooks record file descriptors, socket domain/type/protocol, and socket addresses. Ktrace records socket addresses and successful I/O buffers when enabled.
- `kern_socket()` and `kern_socketpair()` separate descriptor open flags (`O_CLOEXEC`, `O_CLOFORK`) from file/socket status flags (`FNONBLOCK`) before calling socket creation.
- `kern_accept4()` allocates the new file descriptor before dequeuing a completed connection. If dequeue or `soaccept()` fails, it closes the new descriptor and drops references. On success it can either inherit listener file flags/ownership or use explicit `accept4()` flags.
- `kern_connectat()` treats an already-connecting socket as `EALREADY`, maps interrupted restart to `EINTR`, waits on `so_timeo` for blocking connects, and consumes `so_error` after completion.
- `kern_socketpair()` carefully stages two sockets and two files. Its rollback labels close descriptors and call `soclose()` on sockets depending on how far setup progressed.
- Send syscall glue builds a `uio` over the user iovec array, rejects negative accumulated lengths, optionally clones the uio for ktrace, passes ancillary data as mbufs, and stores the successful byte count in `td_retval[0]`.
- Receive syscall glue builds a read `uio`, calls `soreceive()` with optional address/control outputs, turns interrupt/restart/would-block into success when partial data was received, copies out source address and control mbufs, sets `MSG_CTRUNC` on insufficient control buffer space, and disposes externalized rights on truncation/error.
- `sys_recvmsg()` copies the whole message header back to userspace after receive so updated flags, controllen, and namelen are visible.
- `sockargs()` copies user buffers into mbufs for socket addresses or control data, handling old ABI sockaddr-family layout. `getsockaddr()` uses malloc-backed `M_SONAME` storage and enforces maximum/minimum sockaddr sizes.
- `m_dispose_extcontrolm()` walks external-control mbufs, finds `SCM_RIGHTS` file descriptors, closes them from the current thread’s descriptor table, and changes the mbuf type back to `MT_CONTROL` to prevent leaked descriptors after truncation or error.

Important invariants:
- A successfully returned socket descriptor owns exactly one initialized `struct file` pointing at a referenced socket; failed paths must not leave a descriptor or socket reference behind.
- User-provided sockaddrs are copied into kernel memory before protocol calls, and `sa_len` is overwritten with the trusted user buffer length.
- `copyiniov()` is used for `sendmsg()`/`recvmsg()` iovecs, and accumulated `uio_resid` is checked for signed overflow.
- `kern_getsockopt()` treats a NULL output value as zero-length output; negative `socklen_t` values are rejected before casting to `size_t`.
- `kern_setsockopt()` rejects NULL option pointers with nonzero lengths and validates the option buffer address space (`UIO_USERSPACE` vs `UIO_SYSSPACE`) before calling the socket layer.
- Accepted sockets synchronize file flags with socket state using `FIONBIO` and `FIOASYNC` after `finit()`.
- Compatibility code for old socket ABIs is conditional and preserves historical behavior for old sockaddr layout, old control-message rights format, and selected error handling.

Filesystem/OS relevance:
- This file is the descriptor-facing half of the socket subsystem. It bridges the syscall table, file-descriptor table, capability rights, audit/MAC/ktrace subsystems, and the socket core in `uipc_socket.c`. For OS/VFS research, it shows how FreeBSD treats sockets as file objects while routing operations to socket-specific implementations rather than vnode methods.

Notable risks and edge cases:
- Accept and socketpair setup have many partial-allocation failure paths; descriptor close and reference-drop ordering is critical.
- Receive control-message truncation can externalize file descriptors before the user receives them, so `m_dispose_extcontrolm()` is required to prevent descriptor leaks.
- Capability mode rejects path-relative bind/connect operations using `AT_FDCWD`, even when the fd rights check would otherwise pass.
- `kern_shutdown()` intentionally preserves old process behavior for `ENOTCONN`, creating ABI-dependent return values.
- Legacy 4.3BSD compatibility paths alter sockaddr family layout and control message handling, so modern code paths must not assume only one userspace ABI shape.
