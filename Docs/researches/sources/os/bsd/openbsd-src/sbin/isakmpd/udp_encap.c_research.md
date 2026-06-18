# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/udp_encap.c

`udp_encap.c` implements the NAT-T UDP encapsulation transport backend for `isakmpd`. It closely mirrors `udp.c` for socket creation, config-based transport creation, fd integration, reporting, cloning, and send/receive operations, but registers as `udp_encap`.

The transport binds the configured or default NAT-T encapsulation port, usually `UDP_ENCAP_DEFAULT_PORT_STR`, and reuses plain UDP helpers for clone, remove, fd set/isset, source/destination access, and ID decoding. It is connected through `virtual.c`, which switches exchanges between main UDP and encapsulated UDP.

Protocol-specific behavior: receive validates a 32-bit NULL-ESP marker, drops short/nonzero-marker packets, ignores one-byte `0xff` NAT keepalives, strips the marker before message allocation, and marks messages with `MSG_NATT`. Send prefixes real ISAKMP messages with a NULL-ESP marker and sends a one-byte `0xff` marker when called with `msg == NULL`.

Security-relevant details: malformed encapsulated packets are rejected before parser handoff, but the marker check casts the buffer to `u_int32_t *`. Socket binding and cleartext setup follow the same privileged/cleartext path as plain UDP.
