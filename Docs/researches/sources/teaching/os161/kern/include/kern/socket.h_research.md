# File Research: sources/teaching/os161/kern/include/kern/socket.h

Defines socket-related ABI constants and structures.

Key contents:
- Socket types: stream, datagram, raw.
- Address/protocol families: unspecified, Unix, IPv4, IPv6.
- `struct sockaddr` and padded/aligned `struct sockaddr_storage`.
- `struct msghdr` and `struct cmsghdr`.

Relevance:
- Error codes and syscall table include networking support, but listed filesystem files do not implement socket behavior.
