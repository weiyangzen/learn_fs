# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/gre.c

This module decodes GRE headers for RFC 1701/2784 version 0 and PPTP GRE version 1. It supports filtering/demuxing by encapsulated protocol.

`parsehdr` reads flags, protocol, optional checksum/offset, key, sequence, ACK, and source-routing data. `p_filter` consumes the parsed header and matches protocol. `p_seprint` prints version, protocol, flags, optional checksum/key/sequence/ACK/routing offset, and recursion for version 0, then demuxes to protocols such as IP, ARP, PPP, EAPOL, IPv6, or Ethernet.

Notable detail: `parthdrlen` lacks parentheses around additive and ternary terms, so C precedence likely makes its result wrong for some flag combinations. That can affect `parsehdr`’s minimum-length validation.
