# File Research: sources/os/linux/linux/fs/smb/server/transport_tcp.c

Implements ksmbd’s TCP transport: interface binding, listener kthreads, connection accept limits, socket read/write, and network-device event handling.

Key behaviors:
- Tracks configured interfaces with listener socket, listener kthread, name, and state.
- Allocates a `tcp_transport` per client socket, creates a ksmbd connection, records IPv4/IPv6 peer address/hash, and inserts it into the global connection table.
- Accept loop enforces optional per-IP and global max-connection limits before spawning per-connection handler kthreads.
- Configures accepted sockets with receive/send timeouts.
- Implements robust `readv` with retry handling, freezer support, reconnect detection, and connection-alive checks.
- Implements `writev` using `kernel_sendmsg(... MSG_NOSIGNAL)`.
- Creates IPv6 dual-stack listener sockets when possible, falls back to IPv4, sets `TCP_NODELAY`, `SO_REUSEADDR`, and `SO_BINDTODEVICE`, then binds/listens on configured server port.
- Registers a netdevice notifier to start listeners on `NETDEV_UP` and shut them down on `NETDEV_DOWN`.
- Supports “bind all additional interfaces” when startup supplies no explicit interface list.
- Cleans interface list and unregisters notifier on destroy.

Dependencies:
- Uses server config populated by IPC startup, connection allocation/free, auth/connection helpers, kernel socket APIs, and netdevice notifications.

Role in subsystem:
- Default network transport for SMB over TCP, responsible for connection admission and byte-stream I/O before common ksmbd request handling takes over.
