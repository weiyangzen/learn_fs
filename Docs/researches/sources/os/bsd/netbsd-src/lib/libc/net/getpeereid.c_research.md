# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getpeereid.c

Read completely: 68 lines.

This file implements `getpeereid(int s, uid_t *euid, gid_t *egid)` for local-domain sockets. It verifies the socket’s local address family with `getsockname`, rejects non-`AF_LOCAL` sockets with `EOPNOTSUPP`, then fetches peer credentials via `getsockopt(SOL_LOCAL, LOCAL_PEEREID)`.

Security/reliability notes: output pointers are optional. Correctness depends on kernel-provided Unix-domain socket credentials.
