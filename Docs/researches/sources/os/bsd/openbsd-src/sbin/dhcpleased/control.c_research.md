# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/control.c

## Purpose
`control.c` implements the non-`SMALL` local UNIX-domain control socket for runtime management requests to `dhcpleased`.

## Main Responsibilities
- Creates, binds, chmods, and listens on the configured control socket path.
- Accepts nonblocking client connections and wraps each connection in an `imsgev`.
- Tracks active control clients in a `TAILQ`.
- Dispatches control imsgs for reload, verbose logging, interface info, and manual DHCP request/reboot.
- Forwards control requests to main, frontend, and engine processes as needed.
- Relays response imsgs back to the control client matching the original client pid.
- Temporarily pauses accept handling on `ENFILE`/`EMFILE`.

## Important APIs
- `control_init(char *path)`: creates and binds the control socket.
- `control_listen(int fd)`: starts listening and registers libevent handlers.
- `control_accept(...)`: accepts client connections and initializes imsg state.
- `control_dispatch_imsg(...)`: handles requests from clients.
- `control_imsg_relay(struct imsg *)`: forwards process responses back to the requesting client.

## Integration Notes
The frontend owns the control socket event loop after the main process passes the bound fd. Control actions are relayed to the main process or engine through existing frontend imsg plumbing.

## Risk Notes
Client identity for replies is tracked by imsg pid in the connection buffer; concurrent clients depend on consistent pid propagation. Malformed data payloads are ignored for that imsg rather than terminating the daemon.
