# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_generic.c

Read completely: 904 lines.

Provides generic RPC transport, netconfig, socket-info, and universal-address helpers. It maps nettype strings such as `netpath`, `visible`, `circuit_v`, `datagram_n`, `tcp`, and `udp` to internal classes, implements `__rpc_setconf()`/`__rpc_getconf()`/`__rpc_endconf()`, and filters `getnetconfig()` or `getnetpath()` results by visibility, semantics, protocol family, and protocol.

Important helpers include `__rpc_dtbsize()`, `__rpc_get_t_size()`, `__rpc_get_a_size()`, `__rpc_getconfip()`, `rpc_nullproc()`, `__rpcgettp()`, `__rpc_fd2sockinfo()`, `__rpc_nconf2sockinfo()`, `__rpc_nconf2fd()`, `__rpc_sockinfo2netid()`, `__rpc_seman2socktype()`, `__rpc_socktype2seman()`, `__rpc_sockisbound()`, and `__rpc_setnodelay()`.

`taddr2uaddr()`/`uaddr2taddr()` and their address-family helpers convert between transport `netbuf` addresses and RPC universal-address strings for IPv4, optional IPv6, and local sockets. IPv4/IPv6 universal addresses encode the port as two trailing decimal octets. IPv6 scope fixup copies link/site-local scope IDs from the rpcbind service address where possible.

Thread behavior: `__rpc_getconfip()` caches the discovered tcp/udp netids in static storage for single-threaded use and thread-specific storage when threaded. Reliability notes: universal address port parsing uses `atoi()` without strict numeric validation; AF_LOCAL conversion truncates to `sun_path` size by `strncpy()`.
