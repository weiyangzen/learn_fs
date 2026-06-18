# sources/user-network-fs/libfuse/example/service_ll.socket.in

## Purpose
`service_ll.socket.in` is the socket-activation template for the low-level `service_ll` FUSE service.

## Important APIs, Types, and Functions
It defines a systemd socket with `ListenSequentialPacket=@FUSE_SERVICE_SOCKET_DIR_RAW@/service_ll`, `Accept=yes`, `SocketMode=@FUSE_SERVICE_SOCKET_PERMS@`, `RemoveOnStop=yes`, and installation under `sockets.target`.

## Control Flow
Systemd listens on the configured socket and starts a new `service_ll@.service` instance for each accepted connection. The low-level service binary consumes the socket through `fuse_service_accept()`.

## State and Persistence
Runtime state is the socket file and active accepted connections. No filesystem or service state is persisted by the socket unit itself.

## Dependencies and Integration Points
The socket unit must match the service template and libfuse service socket directory. It is the entry point for `mount -t fuse.service_ll ...` style activation.

## Risks
Misconfigured socket path, mode, or missing paired template prevents service activation. Overly permissive socket mode can expose mount service entry points beyond intended users.

## Test Signals
Starting the socket should create the generated path; a mount request should activate `service_ll@.service`; stopping the socket should remove the path.
