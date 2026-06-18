# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/socket_impl.h

## Role

Implementation support header included by `<sys/socket.h>` for basic socket address structure definitions.

## Key Contents

Defines `sa_family_t`, `struct sockaddr`, and, when standards namespace permits, pulls in UNIX-domain and link-layer address support.

Defines `struct sockaddr_storage` with a 256-byte implementation-specific maximum size and alignment padding based on `double`, providing room for common address families such as IPv4, IPv6, and link-layer addresses.

Also defines Linux-compatible `struct sockaddr_ll` and packet type constants for `PF_PACKET` sockets.

## Design Notes

This is the ABI substrate for socket address storage. It deliberately keeps Linux packet socket compatibility visible through normal `<sys/socket.h>` inclusion.
