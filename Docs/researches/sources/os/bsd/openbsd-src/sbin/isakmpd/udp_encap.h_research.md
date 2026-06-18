# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/udp_encap.h

`udp_encap.h` declares the NAT-T UDP encapsulation transport API. It exposes `udp_encap_init()`, `udp_encap_bind()`, and the global `udp_encap_default_port`.

The header is intentionally narrow and relies on the shared `struct udp_transport` from `udp.h`. It is consumed by the virtual transport layer to create and switch to encapsulated transports.
