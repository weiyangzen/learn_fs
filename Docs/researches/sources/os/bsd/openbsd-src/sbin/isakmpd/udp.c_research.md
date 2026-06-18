# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/udp.c

`udp.c` implements the physical UDP transport backend for `isakmpd`. It registers the `udp_physical` transport method, binds UDP sockets, clones listening transports into peer-specific transports, receives ISAKMP packets, and sends messages through `sendmsg()`.

Key paths include `udp_init()`, `udp_bind()`, `udp_make()`, `udp_create()`, `udp_clone()`, `udp_handle_message()`, and `udp_send_message()`. Address and port selection comes from per-peer config, `General:Listen-on`, virtual default transports, and `udp_default_port`.

The socket setup uses `sysdep_cleartext()` to avoid IPsec-encrypting daemon traffic, `SO_REUSEADDR`/`SO_REUSEPORT` depending on wildcard binding, and `monitor_bind()` for privileged bind mediation. Incoming packets on default wildcard virtual transports trigger virtual reinitialization and are dropped because the daemon cannot know the destination address.

Notable coupling: depends on `transport`, `message`, `monitor`, `virtual`, config lookup, sockaddr utilities, and `udp_encap.c`, which reuses several non-static UDP helper functions.
