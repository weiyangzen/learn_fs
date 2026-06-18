# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/ip.c

`snoopy` IPv4 decoder.

Key behavior:
- Parses IPv4 header, including version/IHL, TOS, length, id, fragment, TTL, protocol, checksum, source, and destination.
- Filters on source, destination, either address, or protocol number.
- Demuxes many IP protocol numbers to registered protocol names.
- Suppresses next-protocol decode for non-first fragments.
- Truncates message end to IPv4 total length and prints header options as hex.

Integration:
- Reached from Ethernet, GRE, PPP, ICMP embedded payloads, and other decoders.

Risks and notes:
- Does not validate version or minimum IHL beyond base header availability.
