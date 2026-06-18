# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/frontend.c

## Purpose
`frontend.c` implements the unprivileged interface watcher and packet I/O process for `dhcpleased`.

## Main Responsibilities
- Runs as `_dhcp` with restricted `unveil`/`pledge`.
- Maintains per-interface frontend records with BPF event state, interface metadata, pending DHCP send fields, and optional UDP renewal socket.
- Receives fd-passed route, BPF, UDP, control, and frontend-engine imsg sockets.
- Discovers initial interfaces with `IFXF_AUTOCONF4` via `if_nameindex()`/`getifaddrs()`.
- Watches route socket messages for interface updates, interface departure, and DNS proposal solicit events.
- Requests BPF descriptors from the main process for autoconf-enabled interfaces.
- Reads BPF packets, validates BPF capture headers, and forwards full DHCP candidate packets to the engine.
- Builds DHCPDISCOVER and DHCPREQUEST payloads from engine requests and local config.
- Sends renewals by UDP unicast when a bound UDP socket and server address are available, falling back to BPF broadcast on failure.
- Sends broadcast packets by constructing Ethernet, IPv4, UDP, and DHCP buffers and writing them to BPF.
- Rebuilds frontend config from main-process imsgs and triggers engine reboot requests for changed interface configs.
- Relays control responses between engine/main and control clients.

## Packet Construction
`build_packet()` creates a DHCP BOOTREQUEST with cookie, message type, optional hostname, client identifier, vendor class identifier, parameter request list, requested address, and server identifier. It requests IPv6-only preferred when the interface config says `prefer ipv6`.

## Interface Tracking
`update_iface()` reacts to route `RTM_IFINFO` messages. If `IFXF_AUTOCONF4` is removed, it tells the engine to remove the interface and closes frontend state. Otherwise it updates link/running/rdomain/hardware address information and sends `IMSG_UPDATE_IF` to main.

## Integration Notes
The frontend does not open BPF itself; it asks the main process to do so and receives the descriptor. This allows privilege separation while still performing packet I/O in the unprivileged process.

## Risk Notes
`iface_conf_cmp()` treats any `NULL` hostname on either side as different, so reloads can conservatively trigger DHCP reboot behavior even when other fields are unchanged. DHCP option insertion has comments noting space checks for configured client/vendor IDs, relying on parser-enforced maximum lengths and packet buffer headroom.
