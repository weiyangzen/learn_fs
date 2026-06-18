# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/udp.h

`udp.h` declares the plain UDP transport API and shared state for `isakmpd`. It exposes `udp_init()`, `udp_bind()`, `udp_default_port`, and `bind_family`.

The header defines `BIND_FAMILY_INET4`/`BIND_FAMILY_INET6` filters and `struct udp_transport`, which embeds a generic `struct transport` plus source sockaddr, destination sockaddr, and socket fd.

This file is shared by `udp.c`, `udp_encap.c`, and `virtual.c`; changes affect both plain IKE UDP and NAT-T UDP encapsulation plumbing.
