# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/clnt_bcast.c

Read completely: 689 lines.

This file implements RPC broadcast/multicast client calls: `rpc_broadcast_exp`, `rpc_broadcast`, and helpers for discovering/freeing broadcast interfaces and enabling broadcast.

Key behavior: `__rpc_getbroadifs` uses `getifaddrs` and `getaddrinfo("sunrpc")` to build per-interface IPv4 broadcast or IPv6 RPC multicast destinations. `rpc_broadcast_exp` enumerates datagram netconfig transports, opens sockets, encodes an RPCBPROC_CALLIT request, optionally encodes a legacy PMAPPROC_CALLIT UDP request under `PORTMAP`, sends to all eligible broadcast destinations with exponential wait windows, polls all sockets, matches replies by XID, decodes rpcbind/portmap remote-call results, and invokes `eachresult` until it returns true or timeout expires.

Important interactions: depends on netconfig/rpcbind helpers, AUTH_UNIX default auth, XDR rpcbind/portmap codecs, and interface/address conversion helpers.

Security/reliability notes: broadcast RPC can create duplicate replies and broad network traffic. Reply handling trusts matching XID plus successful RPC decode; result callbacks receive addresses derived from reply content or source port. Interface iteration assumes `ifa_addr` is non-null before dereferencing, which is a sensitive portability edge.
