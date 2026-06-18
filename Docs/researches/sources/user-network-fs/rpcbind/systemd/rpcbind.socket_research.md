<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/systemd/rpcbind.socket -->
# sources/user-network-fs/rpcbind/systemd/rpcbind.socket

Purpose: Concrete systemd socket unit for rpcbind activation on the local unix socket and TCP/UDP port 111 for IPv4 and IPv6.

Important directives: `ListenStream=/run/rpcbind.sock` creates the filesystem unix socket. `BindIPv6Only=ipv6-only` ensures IPv6 sockets are not dual-stack. `ListenStream` and `ListenDatagram` bind `0.0.0.0:111` and `[::]:111`. The unit wants and starts before `rpcbind.target` and installs under `sockets.target`.

Control flow and integration: systemd owns the listening sockets and passes them to `rpcbind.c` through `sd_listen_fds`. The daemon matches each fd against netconfig transport properties and rejects IPv6 dual-mode sockets, so `BindIPv6Only=ipv6-only` is required.

State and persistence: The unit owns socket lifetime while active; no persistent state. The commented abstract unix socket line is disabled in this concrete file.

Dependencies and risks: Requires privileges to bind port 111 and create `/run/rpcbind.sock`. If a distribution modifies IPv6 binding semantics or removes separate sockets, daemon startup can fail. Because it binds wildcard addresses, exposure is controlled by daemon access policy and network firewalls.

Test signals: Use `systemd-analyze verify`, `systemctl start rpcbind.socket`, inspect listening sockets for stream/datagram IPv4 and IPv6 plus unix socket, and confirm daemon activation works for local and network clients.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/systemd/rpcbind.socket -->
