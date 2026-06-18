# File Research: sources/teaching/minix/minix/servers/vfs/socket.c

Implements the upper VFS socket syscall layer: BSD socket calls plus fd/filp/vnode/PipeFS object management.

Key behavior:
- `get_sock_flags` converts `SOCK_CLOEXEC`, `SOCK_NONBLOCK`, and `SOCK_NOSIGPIPE` into open flags.
- `check_sock_fds` performs cheap per-process fd availability checks before creating sockets.
- `make_sock_fd` creates the VFS representation for an open socket: locks PipeFS, allocates vnode and filp/fd, creates a PFS socket node with `REQ_NEWNODE`, fills vnode `v_sdev` with the socket device number, installs the filp, and applies close-on-exec.
- `do_socket` checks domain support through `smap`, asks `sdev_socket` for a socket, and wraps it in a VFS fd, closing the driver socket on wrapping failure.
- `do_socketpair` does the same for two connected sockets, with cleanup for partial fd creation.
- `get_sock` validates a fd as a socket and returns its `dev_t` and filp flags.
- `do_bind`, `do_connect`, `do_listen`, `do_accept`, `do_sendto`, `do_recvfrom`, `do_sockmsg`, option calls, name queries, peer queries, and `do_shutdown` translate syscall messages into lower-layer `sdev_*` calls.

Resume functions:
- `resume_accept` handles failed accept, accepted-but-error, and accepted-success cases. On success it verifies the listening socket, inherits accepted-socket flags, creates the accepted fd with `make_sock_fd`, and replies with fd plus address length.
- `resume_recvfrom` replies with byte count plus address length for successful receives.
- `resume_recvmsg` rereads and rewrites the user `msghdr` to update control length, flags, and optional address length before replying.

Notable implementation details:
- Generic file operations on sockets such as read, write, ioctl, and select bypass this file and go directly to `sdev.c`.
- `do_sockmsg` currently supports at most one iovec element; libc is expected to consolidate vectors.
- Accepted sockets inherit `O_CLOEXEC`, `O_NONBLOCK`, and `O_NOSIGPIPE` from the listening socket.
