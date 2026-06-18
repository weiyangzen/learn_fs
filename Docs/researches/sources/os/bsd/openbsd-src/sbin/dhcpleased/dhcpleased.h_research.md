# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/dhcpleased.h

## Purpose
`dhcpleased.h` is the shared protocol and data definition header for all `dhcpleased` processes.

## Main Contents
- Paths and constants for the lockfile, default config, control socket, daemon user, route label, lease directory, lease file format, and DHCP ports.
- DHCP option codes, message type codes, hardware type constants, and DHCP header layout.
- Limits for DHCP routes, DNS proposals, ignored servers, lease buffer size, domain search length, and DHCP packet string fields.
- Shared `struct imsgev` wrapper combining `imsgbuf`, event handler, libevent object, and event mask.
- `struct dhcp_route` for destination/mask/gateway tuples.
- `enum imsg_type` defining the internal protocol among main, frontend, engine, and control clients.
- Non-`SMALL` config structures: `iface_conf`, `dhcpleased_conf`, and control reporting structure `ctl_engine_info`.
- Wire structures for config transfer, interface info, DNS proposals, DHCP packets, and DHCP send requests.
- Function prototypes shared across main, frontend, engine, parser, and printconf modules.

## Integration Notes
This header is the central contract for imsg payload sizes and semantics. Several structures are copied directly across process boundaries, so layout changes must be coordinated across all three processes.

## Risk Notes
The comment “keep in sync with iface_conf” for `imsg_iface_conf` is important: it intentionally mirrors only the fixed-size subset of interface config before variable-length DHCP option blobs are sent separately.
