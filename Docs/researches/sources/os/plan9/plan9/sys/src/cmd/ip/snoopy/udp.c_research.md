# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/udp.c

`snoopy` UDP decoder.

Key behavior:
- Parses source port, destination port, UDP length, and checksum.
- Filters on source, destination, or either port.
- Demuxes DNS, BOOTP, selected 9P-over-UDP, and optionally RTP/RTCP via `ANYPORT`.
- Formats ports, checksum, and length.

Integration:
- Reached from IPv4/IPv6 UDP protocol numbers.

Risks and notes:
- `defproto` is global mutable state used to support arbitrary-port RTP/RTCP selection during filtering.
- Checksum is printed but not verified.
