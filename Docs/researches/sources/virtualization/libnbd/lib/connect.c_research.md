# File Research: sources/virtualization/libnbd/lib/connect.c

Provides synchronous and asynchronous connection entry points for Unix sockets, vsock, TCP, preconnected sockets, local commands, and systemd socket activation.

Key functions:
- `nbd_internal_wait_until_connected`: polls while the generated state machine is in a connecting group, then validates ready/negotiating/closed/dead outcome.
- Synchronous `nbd_unlocked_connect_*` wrappers: start the matching async connect and wait for completion.
- `nbd_unlocked_aio_connect`: stores a caller-provided sockaddr and starts `cmd_connect_sockaddr`.
- `nbd_unlocked_aio_connect_unix`: validates path length and stores `sockaddr_un`.
- `nbd_unlocked_aio_connect_vsock`: uses `sockaddr_vm` when available, otherwise fails with `ENOTSUP`.
- `nbd_unlocked_aio_connect_tcp`: stores hostname and port strings for generated TCP connection states.
- `nbd_unlocked_aio_connect_socket`: makes caller fd nonblocking and close-on-exec, wraps it in a socket object, then starts handshake directly.
- Command connection functions copy argv then trigger generated command/socket-activation connect states.

Interactions:
- Relies on generated external events such as `cmd_connect_sockaddr`, `cmd_connect_tcp`, `cmd_connect_socket`, `cmd_connect_command`, and `cmd_connect_sa`.
- Uses `utils.c` argv copying and `socket.c` socket wrapping.

Research notes:
- The preconnected socket path takes ownership of the fd on entry; failures close it.
- State validation preserves a previous fatal error if the machine enters DEAD.
