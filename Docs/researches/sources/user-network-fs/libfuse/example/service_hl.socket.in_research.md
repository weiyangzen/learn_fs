# sources/user-network-fs/libfuse/example/service_hl.socket.in

## Purpose
`service_hl.socket.in` is the socket-activation template for the high-level `service_hl` FUSE service.

## Important APIs, Types, and Functions
Key unit settings are `ListenSequentialPacket=@FUSE_SERVICE_SOCKET_DIR_RAW@/service_hl`, `Accept=yes`, `SocketMode=@FUSE_SERVICE_SOCKET_PERMS@`, `RemoveOnStop=yes`, and `WantedBy=sockets.target`.

## Control Flow
Systemd listens on the generated sequential-packet socket. Each accepted connection starts a `service_hl@.service` instance. The service binary receives the socket and uses `fuse_service_accept()` to enter service mode.

## State and Persistence
The socket unit maintains runtime socket state only. Installed unit text is persistent, but mount sessions and accepted sockets are transient.

## Dependencies and Integration Points
The file must be installed with the paired `service_hl@.service` and the configured libfuse service socket directory. It integrates with mount requests for filesystem type `fuse.service_hl`.

## Risks
Incorrect build substitutions or permissions can make service mounts fail or make the service socket accessible to the wrong users. `Accept=yes` requires the template service name and binary path to match.

## Test Signals
`systemctl start service_hl.socket` should create the configured socket. A mount request should spawn `service_hl@...service`, and stopping the socket should remove the socket path.
