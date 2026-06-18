# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/dhcp.c

`snoopy` DHCP option formatter.

Key behavior:
- Walks DHCP option TLVs after BOOTP magic.
- Recognizes DHCP message type, requested IP, lease, server id, message, max message size, client id, parameter request list, vendor class, and many BOOTP options.
- Formats addresses, integers, strings, or hex depending on option type.
- Stops on option `255` and skips pads.

Integration:
- Reached from `bootp.c` when option magic is generic DHCP.

Risks and notes:
- No compile/filter callbacks; formatter only.
- Some printed labels contain typos, e.g. `discovermsak` and `rousupplymaskter`.
