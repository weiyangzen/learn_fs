# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/dhcp6leased.c

Privileged parent process for `dhcp6leased`.

The main daemon parses configuration, supports `-n` syntax/print checking, enforces root and a single-instance lock, verifies the `_dhcp6leased` user, daemonizes unless debugging, forks `engine` and `frontend` child roles via `execvp`, and wires them together with nonblocking imsg socketpairs. It owns privileged resources: route socket for reject routes, IPv6 ioctl socket for address changes, frontend route socket, per-interface UDP socket opening, control socket creation, UUID file creation, and lease-file read/write access.

It sends configuration to both children as imsg object streams, passes the frontend/engine IPC socketpair, passes route/control/UDP sockets by descriptor, and broadcasts a stable DUID UUID loaded from or atomically written to `/var/db/dhcp6leased/uuid`. It uses `unveil()` and `pledge()` after setup; if lease-directory unveil fails, it disables lease-file persistence.

The parent handles child messages to open DHCPv6 UDP sockets bound to an interface link-local address and routing domain, configure/deconfigure IPv6 addresses with `SIOCAIFADDR_IN6`/`SIOCDIFADDR_IN6`, add/delete static reject routes labeled `dhcp6leased`, and atomically write per-interface lease files. It also reads saved leases during interface updates so the engine can attempt reboot/rebind behavior.
