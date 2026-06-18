# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/ipconfig/ipv6.c

Implements IPv6 address autoconfiguration, router solicitation reception, router advertisement sending/receiving, and RA control-file updates for `ipconfig`.

Key behavior:
- Defines IPv6 multicast, unspecified, loopback, global-unicast, link-local, solicited-node, and default-mask addresses.
- `ea2lla` converts Ethernet MAC to link-local IPv6 address using EUI-64 expansion.
- `ipv62smcast` builds solicited-node multicast address.
- `v6paraminit` initializes default RA and prefix parameters.
- `dialicmp` opens `/net/icmpv6` connections in header mode.
- `ip6cfg` adds an IPv6 address to an interface, optionally autogenerating link-local, and can perform duplicate neighbor discovery by checking the ARP cache after a `try`.
- `recvrahost` consumes router advertisements, updates RA params, ARP neighbor entry for source link-layer address, MTU, and prefix settings via `add6`.
- `recvra6` forks a daemon that sends initial router solicitations and processes router advertisements according to interface `recvra6`/`sendra6` state.
- `recvrs` parses router solicitations and updates ARP from source link-layer option.
- `sendra` builds router advertisements from current interface global unicast prefixes and MAC address.
- `sendra6` forks a daemon that responds to solicitations and sends periodic/final RAs.
- `startra6` starts RA daemons and enables IP routing when advertising.
- `doipv6` is the CLI entry for `add6` and `ra6` actions.

Integration points:
- Uses Plan 9 IP interface introspection `readipifc`, control-file writes to `ipifc/ctl`, and ARP control updates.
- Shares global `conf`, `myifc`, `nip`, `dolog`, `debug`.

Risks and notes:
- Packet option parsing trusts option length fields enough to advance through the packet; several cases validate expected sizes but default/ignored paths just skip `8 * len`.
- Router mode currently only logs received RAs from other routers.
- Duplicate detection is coarse: after `try`, it scans the ARP table for the configured address string.
