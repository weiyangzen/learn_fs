# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/slaacd.c

Main `slaacd` supervisor and privileged executor. It starts the frontend and engine children, wires imsg channels, owns privileged sockets/ioctls/route writes, and handles kernel state mutation requested by the engine.

Startup:
- Supports normal mode plus internal `-E` and `-F` child modes.
- Requires root, uses `/dev/slaacd.lock` with exclusive nonblocking lock, validates `_slaacd`, daemonizes unless `-d`.
- Creates socketpairs for main-frontend and main-engine, forks/execs child modes, then passes an additional frontend-engine socketpair via imsg.
- Opens route sockets, ioctl socket, and optional control socket; sets route message/table filters for the frontend route socket.
- Reads `/etc/soii.key` into the global SOII key in non-`SMALL` builds.
- Pledges `stdio inet sendfd wroute`.

Privileged operations:
- `open_icmp6sock()` opens raw ICMPv6 sockets per rdomain, enables packet info and hop-limit ancillary data, sets `SO_RTABLE`, and passes fds to frontend.
- `configure_interface()` performs `SIOCAIFADDR_IN6`, setting address, destination router, prefix mask, lifetimes, `IN6_IFF_AUTOCONF`, optional `IN6_IFF_TEMPORARY`, and optional MTU via `SIOCSIFMTU`.
- `delete_address()` removes IPv6 addresses with `SIOCDIFADDR_IN6`.
- `configure_gateway()` builds route messages with destination `::/0`, gateway, netmask, route label `slaacd`, and writes `RTM_ADD`/`RTM_DELETE`.
- `send_rdns_proposal()` writes `RTM_PROPOSAL` messages containing DNS server proposals.

Imsg topology:
- Main receives interface updates and socket-open requests from frontend.
- Main forwards interface updates to engine after filling SOII key.
- Main receives address/route/RDNS configuration proposals from engine and mutates kernel state.
- Helpers `imsg_event_add()`, `imsg_compose_event()`, and `imsg_forward_event()` integrate imsg buffers with libevent.

Shutdown:
- Closes child pipes, waits for children, logs abnormal child signals, frees imsgev state, and exits.

Utility functions:
- `sin6_to_str()` formats IPv6 sockaddr values.
- Hex parsing supports SOII key loading.
- `i2s()` maps imsg type constants to strings for diagnostics.

Filesystem/storage relevance:
- No filesystem implementation. It is important OS plumbing: privilege separation, raw sockets, route messages, ioctl mutation, lock-file single-instance control, and config-key file reading.
