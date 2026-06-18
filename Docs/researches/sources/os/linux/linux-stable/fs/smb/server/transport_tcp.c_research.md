# File Research: sources/os/linux/linux-stable/fs/smb/server/transport_tcp.c

## Summary
Implements ksmbd’s TCP transport listener and per-connection socket I/O. It manages configured network interfaces, accepts SMB clients, enforces global and per-IP connection limits, creates ksmbd connection threads, reads/writes SMB messages, and responds to netdevice up/down events.

## Main Responsibilities
- Track configured interfaces and dynamically bind additional interfaces when requested.
- Create IPv6 dual-stack sockets with IPv4 fallback, bind to `server_conf.tcp_port`, set `SO_BINDTODEVICE`, enable reuseaddr/nodelay, and listen.
- Accept client sockets in per-interface listener kthreads.
- Enforce `server_conf.max_connections` and `server_conf.max_ip_connections`.
- Allocate `struct tcp_transport`, associate it with `struct ksmbd_conn`, populate IPv4/IPv6 peer identity and connection hash, and start `ksmbd_conn_handler_loop`.
- Provide transport `read`, `writev`, `disconnect`, and `free_transport` operations.
- Read exact byte counts with retry handling, freezer support, reconnect/shutdown checks, and reusable kvec arrays.
- Register a netdevice notifier to create sockets on interface up and tear them down on interface down.

## Key Interfaces
`ksmbd_tcp_set_interfaces()`, `ksmbd_find_netdev_name_iface_list()`, `ksmbd_free_transport()`, `ksmbd_tcp_init()`, and `ksmbd_tcp_destroy()`.

## Important Behavior
If the daemon provides no interface list, `bind_additional_ifaces` is enabled and sockets are created for suitable interfaces as they appear. If an interface list is provided, only those names are tracked. Accepted sockets get receive/send timeouts and then are handed to per-client ksmbd threads.

`ksmbd_tcp_readv()` retries `-ERESTARTSYS`/`-EAGAIN` according to `max_retries`, supports unlimited retries for inactive sessions, and returns shutdown/reconnect errors when connection state changes.

## Cross-File Interactions
Configured by IPC startup, used by server lifecycle, and integrated with the common connection handler through `ksmbd_transport_ops`.

## Risks
Connection accounting must stay balanced on accept failure, new-connection failure, and disconnect. Netdevice down handling must stop listener threads and release sockets without racing accept. Read retry behavior affects idle sessions and teardown responsiveness.
