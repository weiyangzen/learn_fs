## sources/user-network-fs/libtirpc/src/clnt_bcast.c

Purpose: Implements RPC broadcast discovery through `rpc_broadcast_exp` and `rpc_broadcast`, sending `RPCBPROC_CALLIT` requests over datagram transports and invoking a caller callback for each reply.

Important APIs and control flow: `__rpc_getbroadifs` enumerates active interfaces with `getifaddrs`, finds the sunrpc service port via `getaddrinfo`, and builds a TAILQ of IPv4 broadcast or IPv6 multicast destinations. `rpc_broadcast_exp` selects `datagram_n` by default, iterates `__rpc_setconf` results, opens sockets, builds RPCB and optionally legacy PMAP call packets, then repeatedly sends to each broadcast address and polls for replies with expanding waits. Matching replies are decoded with `xdr_replymsg`; successful responses are converted from universal address to `netbuf` and passed to `eachresult`.

State and persistence: Owns only stack arrays and temporary buffers; `__rpc_lowvers` globally controls whether only old portmapper broadcasts are sent.

Dependencies and integration: Integrates with netconfig, rpcbind XDR, optional PORTMAP compatibility, `authunix_create_default`, and debug logging.

Risks and test signals: Broadcast storms, duplicate rpcbind/portmap replies, address-family fixups, and callback-controlled early exit are key risks. Tests should mock datagram sockets, malformed replies, IPv6-v4 fixup, callback false/true behavior, and cleanup of all sockets/interface lists.
