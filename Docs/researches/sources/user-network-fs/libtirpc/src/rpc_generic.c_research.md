<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_generic.c -->
# sources/user-network-fs/libtirpc/src/rpc_generic.c

Purpose: shared RPC transport utility layer. It maps netconfig entries to sockets and addresses, iterates nettype selectors, converts between transport addresses and universal addresses, computes buffer sizes, and provides small compatibility helpers.

Important APIs and functions: `__rpc_dtbsize()` caches `RLIMIT_NOFILE`; `__rpc_get_t_size()` and `__rpc_get_a_size()` choose transport/address buffer sizes; `__rpc_getconfip()` finds cached IPv4 tcp/udp netconfig entries in thread-specific storage; `__rpc_setconf()`, `__rpc_getconf()`, and `__rpc_endconf()` implement nettype iteration. `rpc_nullproc()` pings NULLPROC. `__rpcgettp()`, `__rpc_fd2sockinfo()`, `__rpc_nconf2sockinfo()`, `__rpc_nconf2fd_flags()`, `__rpc_nconf2fd()`, and `__rpc_sockinfo2netid()` bridge descriptors, netconfig, and socket metadata. `taddr2uaddr()`, `uaddr2taddr()`, `__rpc_taddr2uaddr_af()`, and `__rpc_uaddr2taddr_af()` handle universal address encoding. `__rpc_fixup_addr()` preserves IPv6 scope IDs. `__rpc_sockisbound()` tests whether a descriptor has a usable bound address. `__rpc_set_netbuf()` reallocates/copies a `netbuf`.

Control flow: nettype strings are mapped to internal enum values, then `__rpc_getconf()` filters `getnetpath()` or `getnetconfig()` results by visibility, semantics, protocol family, and protocol. Socket creation derives family/type/protocol from netconfig and sets IPv6-only on IPv6 sockets. Universal address conversion formats IPv4/IPv6 as address plus two decimal port octets and local sockets as path/abstract names; decoding reverses this into allocated `netbuf` and sockaddr objects.

State and persistence: caches descriptor-table size in `__rpc_dtbsize`; caches tcp/udp netids in thread-specific keys; returned netconfig entries and address buffers are heap allocations requiring caller cleanup. `__rpc_set_netbuf()` owns/replaces the destination netbuf buffer via `mem_alloc`/`mem_free`.

Dependencies and integration points: depends on netconfig/netpath, sockets, `inet_ntop`/`inet_pton`, pthread/TSD compatibility wrappers, and `rpc_com.h`. It is foundational for `rpcb_clnt.c`, `svc_generic.c`, `svc_dg.c`, and `rpc_soc.c`.

Risks: universal-address parsing uses `atoi` for port octets without strict range validation. AF_LOCAL conversion truncates long paths through `strncpy`. Thread-specific netid caching depends on global key initialization locks. `__rpc_nconf2fd_flags()` silently ignores IPv6-only `setsockopt` failure.

Test signals: nettype iteration for `netpath`, visible, tcp, udp, circuit, and datagram filters; IPv4/IPv6/local universal address round trips; invalid universal addresses; descriptor-to-netid mapping; IPv6 link-local scope fixups; bound/unbound sockets; and memory cleanup of netbuf replacements.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpc_generic.c -->
