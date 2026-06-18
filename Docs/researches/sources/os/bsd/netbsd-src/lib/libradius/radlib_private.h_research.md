# File Research: sources/os/bsd/netbsd-src/lib/libradius/radlib_private.h

This private RADIUS header defines implementation constants and internal state structures. It includes the public RADIUS header and vendor-specific header.

Handle type constants distinguish authentication and accounting. Defaults include max tries, config path `/etc/radius.conf`, standard RADIUS and accounting UDP ports, and timeout. Limits define error-message length, config line length, max server count, max message size, and significant password size. Packet offsets define code, identifier, length, authenticator, authenticator length, and start of attributes.

`struct rad_server` stores a server sockaddr, shared secret, timeout, maximum tries, and current try count. `struct rad_handle` stores the socket fd, server array and count, current identifier, last error, request buffer and length, cleartext password scratch state, CHAP/EAP/authenticator flags, response buffer and scan position, retry counters, selected server index, and handle type.

`struct vendor_attribute` is the packed-in-practice layout used to construct and parse RADIUS vendor-specific attribute payloads: vendor id, nested attribute type, nested length, and data.
