# File Research: sources/os/bsd/openbsd-src/sys/kern/uipc_proto.c

UNIX-domain protocol switch table.

This file declares the `unixsw[]` protocol entries for `SOCK_STREAM`, `SOCK_SEQPACKET`, and `SOCK_DGRAM` in the UNIX domain. Stream sockets are connection-required, want receive notifications, and support rights passing. Seqpacket sockets add atomic record semantics. Datagram sockets are atomic, include sender addresses, and use the datagram-specific request vector.

It also declares `unixdomain`, the `AF_UNIX` domain descriptor. The domain initializes through `unp_init()`, externalizes/disposes ancillary rights through `unp_externalize()` and `unp_dispose()`, and points at the `unixsw[]` range for lookup by the generic domain code.

Notable constraints: all UNIX-domain protocol entries advertise `PR_RIGHTS`, which is why socket receive and release paths must call domain dispose/externalize hooks for control messages.
