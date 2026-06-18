# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/socket_proto.h

## Role

Kernel-facing protocol interface between sockfs and socket protocol providers.

## Key Contents

Defines `sock_connid_t` generation counters and comparison helpers. Defines `struct sock_proto_props`, which transports protocol properties such as write offset, watermarks, max/min packet size, zero-copy flags, OOB behavior, receive timer/threshold, maximum address length, and loopback status.

## Kernel Interfaces

Defines opaque upper/lower handles, `sock_downcalls_t` for sockfs-to-protocol operations, and `sock_upcalls_t` for protocol-to-sockfs notifications. Downcalls cover activate, accept, bind, listen, connect, names, options, send/receive, poll, shutdown, ioctl, and close. Upcalls cover new connections, connected/disconnected state, receive delivery, protocol property changes, flow control, OOB notification, zero-copy completion, errors, close, and vnode lookup.

Also declares standard `*_notsupp` helpers returning unsupported-operation behavior.

## Design Notes

The version macros are `sizeof` the upcall/downcall structures, making ABI compatibility sensitive to structure layout.
