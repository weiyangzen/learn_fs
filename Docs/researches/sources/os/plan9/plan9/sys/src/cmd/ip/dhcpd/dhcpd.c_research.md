# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/dhcpd.c

`dhcpd.c` is the main Plan 9 DHCP/BOOTP server.

Key behavior:
- Usage supports debug, mute, no-BOOTP, PPTP-only, slow response modes, lease tuning, v6 Plan 9 vendor options, network mount point, NDB file, and dynamic address ranges.
- Maintains per-request `Req` state with parsed BOOTP/DHCP data, relay/client addresses, requested options, NDB info, and reply buffer state.
- `proto` validates packet shape, detects Plan 9/generic option cookies, parses options, derives client id, looks up gateway/client info, and dispatches DHCP vs BOOTP.
- DHCP handlers implement Discover, Request, Decline, Release, and Inform behavior, using static NDB bindings or dynamic lease database bindings.
- `sendoffer`, `sendack`, and `sendnak` construct replies, choose unicast/broadcast/relay destinations, update ARP for direct replies, and emit options.
- `bootp` handles legacy BOOTP, Plan 9 vendor fields, generic RFC1048 options, boot file selection, TFTP server selection, and reply padding.
- `parseoptions` handles requested IP, lease, type, server id, message, max message, client id, params, and vendor class.
- `miscoptions` supplies mask/router/domain/rootpath and requested server options from NDB; adds Plan 9-specific vendor data for Plan 9 clients.
- Provides option encoding helpers, logging, passive queue-draining read logic, ARP entry insertion, and access to system name.

Important dependencies:
- Uses `db.c` for dynamic leases, `ndb.c` for host/network lookups, `ping.c` for address probing, and `dhcp.h` protocol definitions.

Notable risks/quirks:
- Single-threaded server intentionally stops listening while sleeping in slow modes.
- Uses filesystem lease files for synchronization rather than in-process locks.
- Some BOOTP/vendor behavior is highly Plan 9-specific.
