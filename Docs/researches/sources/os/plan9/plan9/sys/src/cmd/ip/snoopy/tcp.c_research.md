# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/tcp.c

`snoopy` TCP decoder.

Key behavior:
- Parses source/destination ports, sequence, ack, flags/header length, window, checksum, urgent pointer, and options.
- Filters on source, destination, or either port.
- Demuxes selected ports to DNS and 9P.
- Formats flags and common options: MSS, window scale, EOL, NOOP, and generic options.

Integration:
- Reached from IPv4/IPv6 TCP protocol numbers.

Risks and notes:
- Header length is computed from flag word; short/malformed header length can advance `m->ps` inconsistently.
- Checksum is printed but not verified.
