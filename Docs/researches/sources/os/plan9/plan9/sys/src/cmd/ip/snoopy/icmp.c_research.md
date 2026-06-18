# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/icmp.c

`snoopy` ICMPv4 decoder.

Key behavior:
- Parses ICMP type, code, checksum, and type-specific payload.
- Filters on ICMP type or embedded IP-bearing error messages.
- Demuxes error messages containing original IP header back to `ip`.
- Formats type names, echo id/sequence, timestamp fields, redirect gateway, and parameter pointer.
- Optional checksum verification when `Cflag` is set.

Integration:
- Reached from IPv4 protocol number 1.

Risks and notes:
- `p_seprint()` advances before checking minimum remaining size, but still catches short packets later.
