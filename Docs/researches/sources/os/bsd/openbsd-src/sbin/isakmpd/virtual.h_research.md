# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/virtual.h

`virtual.h` declares the virtual UDP transport wrapper for `isakmpd`. `struct virtual_transport` embeds a generic transport, pointers to the main UDP and NAT-T encapsulated transports, an `encap_is_active` switch, and a listener-list link.

The header exports `virtual_init()`, `virtual_get_default()`, and `virtual_listen_lookup()`. It is the bridge between configured peer transports and actual per-address UDP sockets.
