# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipsend/dlcommon.c

This file provides shared DLPI test and utility routines for STREAMS/DLPI backends.

It implements request helpers for DLPI primitives such as info, attach, bind, unbind, detach, multicast enable/disable, promiscuous mode, physical address get/set, and unitdata send. It also implements acknowledgement readers and validators for info, ok, error, bind, and physical-address acknowledgements.

`strgetmsg()` wraps `getmsg()` with an alarm timeout, checks `MORECTL`/`MOREDATA`, and validates a minimum control length. `expecting()` verifies the returned primitive type.

A large portion of the file formats DLPI primitives into human-readable output: info, bind, unitdata, errors, test/xid messages, QoS, address buffers, primitive names, states, errno names, promiscuous levels, service modes, provider styles, and MAC types.

The file uses old K&R-style definitions in many places and is written for portability to legacy UNIX DLPI systems.

Important dependencies include `<sys/dlpi.h>`, STREAMS headers, `dltest.h`, and helper functions `err()`/`syserr()` defined in this file.

Implementation notes and risks:
- Several functions lack explicit return types, reflecting legacy C.
- Some primitive construction appears suspicious, such as disable-multicast/set-physical-address request code using `DL_ENABMULTI_REQ` constants.
- `printdlxidind` has malformed-looking parameter text in this source, indicating historically fragile code.
- Error handling generally terminates the process.
