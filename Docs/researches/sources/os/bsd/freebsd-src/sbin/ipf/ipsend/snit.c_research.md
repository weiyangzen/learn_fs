# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/snit.c

This is the SunOS NIT output backend for `ipsend`.

`initdevice()` opens `/dev/nit`, configures STREAMS options, pushes `nbuf`, sets a timeout with `NIOCSTIME`, and binds to the requested interface with `NIOCBIND`.

`sendip()` expects an Ethernet-framed packet, splits the destination link-layer address into a `sockaddr` control message, sends the remaining packet data through `putmsg()`, and flushes the write queue.

Important dependencies include Sun NIT headers, STREAMS, Ethernet/IP headers, and `ipsend.h`.

Implementation notes and risks:
- Legacy SunOS-only code.
- Assumes an Ethernet-like header and minimum frame size.
- Error handling exits or returns `-1` depending on phase.
