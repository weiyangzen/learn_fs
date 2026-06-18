# File Research: sources/os/bsd/openbsd-src/sbin/slaacd/frontend.c

Implements the `slaacd` frontend process: observes interfaces, route-socket events, ICMPv6 router advertisements, and control connections, then forwards normalized facts to the engine/main process.

Process setup:
- Drops privileges to `_slaacd`, unveils `/` with no permissions, pledges `stdio unix recvfd route`.
- Receives route socket, control socket, frontend-engine IPC socket, and ICMPv6 sockets by imsg fd passing.
- Maintains `interfaces` and per-rdomain shared `icmp6_ev` receivers.

Interface discovery:
- `frontend_startup()` enables route-socket event handling and scans all interfaces via `if_nameindex()`.
- `update_iface()` reads flags (`SIOCGIFFLAGS`), extended flags (`SIOCGIFXFLAGS`), routing domain (`SIOCGIFRDOMAIN`), link state, Ethernet address, link-local IPv6 address, autoconf/temp flags, and SOII flag.
- Defers solicitation until the link-local address is no longer tentative.

Route socket handling:
- `route_receive()` reads route messages, validates length/version, expands route socket addresses with `get_rtaddrs()`, and dispatches by message type.
- `handle_route_message()` handles:
  - `RTM_IFINFO`: update or remove interface based on autoconf flags.
  - `RTM_IFANNOUNCE`: remove departed interfaces.
  - `RTM_NEWADDR`: refresh interface facts.
  - `RTM_DELADDR`: notify engine of deleted IPv6 addresses.
  - `RTM_CHGADDRATTR`: detect duplicated autoconf addresses and notify engine.
  - `RTM_DELETE`: detect removal of `slaacd`-labelled default routes.
  - `RTM_PROPOSAL`: repropose RDNS on resolver solicitation.

ICMPv6 handling:
- `get_icmp6ev_by_rdomain()` allocates one raw ICMPv6 receive event per routing domain and asks main to open the privileged socket.
- `set_icmp6sock()` attaches the passed raw socket to waiting interfaces.
- `icmp6_receive()` only forwards router advertisements with a receiving interface, hop limit 255, and bounded packet length.
- `send_solicitation()` sends ND router solicitations to `ff02::2` using packet info, hop limit 255, and source link-layer address.

Control relay:
- In non-`SMALL` builds, forwards control fd setup to `control_listen()` and relays engine control responses back to control clients.

Filesystem/storage relevance:
- No filesystem logic. Relevant as an OpenBSD route-socket and raw-socket daemon frontend with privilege separation and routing-domain aware resource sharing.
