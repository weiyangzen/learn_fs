# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/engine.c

## Purpose
`engine.c` implements the unprivileged DHCP state machine, lease interpretation, timers, and decisions about when to request, configure, renew, rebind, deconfigure, or enter IPv6-only mode.

## Main Responsibilities
- Runs as the `_dhcp` user with restricted `unveil`/`pledge`.
- Maintains a list of `dhcpleased_iface` state objects keyed by interface index.
- Receives interface state updates from the main process and DHCP packets from the frontend.
- Parses incoming Ethernet/IP/UDP/DHCP packets and validates destination MAC, IP checksum, UDP checksum, DHCP cookie, xid, and option lengths.
- Handles DHCPOFFER, DHCPACK, and DHCPNAK according to current interface state.
- Tracks lease times, renewal time, rebinding time, server identifier, requested address, subnet mask, routes, DNS servers, boot file, hostname, and domain name.
- Implements RFC 2131 retry/backoff behavior for discover/request/renew/rebind flows.
- Supports RFC 8925 IPv6-only preferred option, enforcing a minimum wait time.
- Honors config options to ignore DNS, ignore routes, ignore specific servers, and prefer IPv6.
- Sends main-process requests to configure/deconfigure addresses, withdraw routes, and propose/withdraw DNS.
- Sends frontend requests to transmit DHCPDISCOVER or DHCPREQUEST.
- Serves control-socket interface-info requests in non-`SMALL` builds.

## State Machine
States are:
- `IF_DOWN`
- `IF_INIT`
- `IF_REQUESTING`
- `IF_BOUND`
- `IF_RENEWING`
- `IF_REBINDING`
- `IF_REBOOTING`
- `IF_IPV6_ONLY`

`state_transition()` sets timers and side effects. `iface_timeout()` advances retries, renewals, rebinding, expiry, and IPv6-only wait completion.

## Packet and Option Parsing
Recognized DHCP options include message type, server identifier, lease time, subnet mask, routers, DNS servers, hostname, domain name, renewal/rebinding time, client identifier, classless static routes, and IPv6-only preferred. Classless static routes override router options per RFC 3442. Unknown options are skipped with verbose debug logging.

## Integration Notes
The engine never directly mutates the system. It sends desired actions to the privileged main process and send-packet requests to the frontend. This keeps packet parsing and lease policy mostly unprivileged.

## Risk Notes
Malformed child/main/frontend imsg protocol is fatal. Incoming network packets are handled defensively and usually logged/ignored on validation failure. `send_rdns_proposal()` logs and sends even when the nameserver list is empty; withdrawal uses a separate imsg type with count zero.
