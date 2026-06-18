# File Research: sources/os/bsd/netbsd-src/lib/libc/net/sctp_sys_calls.c

Userland SCTP convenience wrappers around ioctls, socket options, `sendmsg()`, and `recvmsg()`. It implements address conversion for IPv4-mapped IPv6, multi-address connect/bind helpers, association ID lookup, peer/local address list retrieval and freeing, send/receive helpers, `sctp_recvv()`, `sctp_sendv()`, and `sctp_peeloff()`.

The send wrappers build SCTP control messages such as `SCTP_SNDRCV`, `SCTP_SNDINFO`, `SCTP_PRINFO`, `SCTP_AUTHINFO`, and destination-address ancillary data. The receive wrappers scan returned control messages for SCTP metadata and copy the requested receive info shape when the caller supplied enough storage.

The address-list functions return pointers into allocated `struct sctp_getaddresses` buffers and the matching free functions subtract the hidden header offset before freeing.
