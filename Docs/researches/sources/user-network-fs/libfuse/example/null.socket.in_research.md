# sources/user-network-fs/libfuse/example/null.socket.in

## Purpose
`null.socket.in` is the systemd socket-activation unit template for the `null` sample FUSE service. It creates an accepting Unix sequential-packet socket in the configured FUSE service socket directory.

## Important APIs, Types, and Functions
This is a systemd unit, not C code. Key settings are `ListenSequentialPacket=@FUSE_SERVICE_SOCKET_DIR_RAW@/null`, `Accept=yes`, `SocketMode=@FUSE_SERVICE_SOCKET_PERMS@`, `RemoveOnStop=yes`, and `WantedBy=sockets.target`. The `@...@` tokens are build-time substitutions.

## Control Flow
When the socket unit starts, systemd listens at the generated path. Each accepted connection starts an instance of the paired `null@.service`, passing the accepted socket to the service process. `RemoveOnStop=yes` removes the socket path when the unit stops.

## State and Persistence
The runtime state is the systemd socket inode and accepted connections. There is no persistent state beyond the installed unit file. The socket path and mode are determined by configure-time substitutions and systemd's unit state.

## Dependencies and Integration Points
This file integrates with `null.c` through `fuse_service_accept()` and with `null@.service` through `Accept=yes` instance activation. It depends on systemd support for Unix sequential-packet sockets and on the libfuse service socket directory convention.

## Risks
Bad substitution values for socket directory or permissions can prevent mounting or expose the socket too broadly. Because `Accept=yes` creates per-connection service instances, the service template must be installed with the expected name and `ExecStart` must point to the compiled binary.

## Test Signals
After installation and `systemctl daemon-reload`, `systemctl start null.socket` should create the configured socket. A service-mode FUSE mount should cause an instance of `null@.service` to start, and stopping the socket should remove the socket path.
