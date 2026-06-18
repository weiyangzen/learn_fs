# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/snoopy/gre.c

`snoopy` GRE decoder for RFC 1701/2784 and PPTP-style GRE.

Key behavior:
- Parses GRE flags, protocol, optional checksum/offset, key, sequence, ack, and routing blocks.
- Filters/demuxes on encapsulated protocol.
- Demuxes common encapsulated protocol values including IP, ARP, PPP, EAPOL, and VLAN.
- Formats version, protocol, flags, and present optional fields.

Integration:
- Reached from IPv4/IPv6 protocol number 47.

Risks and notes:
- `parthdrlen()` has operator-precedence problems; as written it likely returns `4` for most flag combinations instead of adding optional field sizes.
- Routing skip loop does not advance past the final zero-length routing marker.
