# File Research: sources/os/bsd/openbsd-src/sbin/unwind/unwind.c

This is the main supervisor for OpenBSD `unwind`, a privilege-separated DNS resolver daemon. It parses command-line options, validates configuration, daemonizes when not in debug mode, creates IPC socketpairs, starts resolver and frontend child processes, and then drives the main libevent loop.

Key behavior:
- Supports main, resolver-child, and frontend-child modes through `-E` and `-F`.
- Uses `imsg` with fd passing to connect main, frontend, and resolver processes.
- Opens loopback DNS sockets for UDP/TCP IPv4 and IPv6 and passes them to the frontend.
- Creates and passes control, route, trust-anchor, and blocklist fds.
- Handles reload by parsing a fresh config, sending it to children, then merging it into the live `main_conf`.
- Handles shutdown by clearing imsg buffers, closing fds, freeing config, and waiting for children.

Important structures/functions:
- `main()`: daemon setup, child spawning, fd setup, pledge, startup signaling.
- `start_child()`: forks and re-execs self with child role flags.
- `main_dispatch_frontend()` / `main_dispatch_resolver()`: parent-side imsg dispatch.
- `main_imsg_send_config()`: serializes config across imsg messages.
- `merge_config()` / `config_clear()` / `config_new_empty()`: live config ownership and cleanup.
- `open_ports()`: binds localhost DNS sockets.
- `solicit_dns_proposals()`: emits routing proposal solicitation.
- `imsg_receive_config()`: shared config deserializer used by child processes.

Filesystem/OS relevance:
- Uses `/etc/unwind.conf`, `/var/db/unwind.key`, `/dev/unwind.sock`, and optional blocklist files.
- Exercises OpenBSD process privilege separation, route sockets, pledge, fd passing, daemon lifecycle, and config reload semantics.
