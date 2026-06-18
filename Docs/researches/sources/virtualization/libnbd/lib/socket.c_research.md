# File Research: sources/virtualization/libnbd/lib/socket.c

Plain Berkeley socket implementation of `struct socket_ops`.

Key functions:
- `socket_recv`: wraps `recv`, setting libnbd error except for nonblocking retry errors.
- `socket_send`: adds `MSG_NOSIGNAL`, wraps `send`, and avoids process-wide SIGPIPE handler changes.
- `socket_get_fd`: returns fd.
- `socket_shut_writes`: calls `shutdown(SHUT_WR)` and ignores failures after debug logging.
- `socket_close`: closes fd and frees wrapper.
- `nbd_internal_socket_create`: allocates socket wrapper and installs ops.

Interactions:
- `connect.c` wraps preconnected sockets with this.
- `crypto.c` wraps this socket with TLS ops after STARTTLS.

Research notes:
- `pending` is not supplied for plain sockets; TLS supplies it because decrypted data may be buffered inside GnuTLS.
