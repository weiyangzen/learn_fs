# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/icmp6.c

`snoopy` ICMPv6 and neighbor-discovery decoder.

Key behavior:
- Parses ICMPv6 type, code, checksum, and data.
- Filters on type or embedded IPv6-bearing error messages.
- Formats unreachable, packet-too-big, time-exceeded, parameter-problem, echo, router solicit/advert, neighbor solicit/advert, redirect, timestamp, and info messages.
- `opt_seprint()` decodes ND options: source/target link-layer, prefix information, redirect, and MTU.
- Demuxes selected errors and redirects to `ip6`.

Integration:
- Reached from IPv6 next-header 58.

Risks and notes:
- Checksum verification is present but commented out.
- Parameter-problem bounds check uses `>` rather than `>=` against `nelem(parpcode)`.
