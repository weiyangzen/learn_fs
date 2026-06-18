<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpcb_clnt.c -->
# sources/user-network-fs/libtirpc/src/rpcb_clnt.c

Purpose: client interface to the rpcbind service, including mapping registration, address lookup, remote call, time lookup, address conversion fallbacks, and an rpcbind-address cache.

Important APIs and functions: public/internal APIs include `__rpc_control()`, `rpcb_set()`, `rpcb_unset()`, `__rpcb_findaddr_timed()`, `rpcb_getaddr()`, `rpcb_getmaps()`, `rpcb_rmtcall()`, `rpcb_gettime()`, `rpcb_taddr2uaddr()`, and `rpcb_uaddr2taddr()`. Key helpers include address-cache routines, `getclnthandle()`, `getpmaphandle()`, `local_rpcb()`, and, under `PORTMAP`, `__try_protocol_version_2()`.

Control flow: rpcbind client creation checks the host/netid cache, deep-copies cache entries under a mutex, tries `clnt_tli_create`, and deletes failed cached addresses. Without a usable cache, it resolves the rpcbind service via local Unix sockets for loopback transports or `getaddrinfo(host, "sunrpc")` for remote hosts, then stores successful target addresses. Registration/unregistration always uses local rpcbind. Address lookup creates or reuses a client, tries rpcbind v4 then v3 for `RPCBPROC_GETADDR`, translates universal addresses to transport addresses, fixes IPv6 scope IDs, and optionally falls back to portmapper v2 for IPv4 TCP/UDP. `rpcb_rmtcall()` tries rpcbind v4/v3 `RPCBPROC_CALLIT`, translates the returned universal address, and copies it into caller-provided storage when requested.

State and persistence: stores a six-entry process-global LRU-ish `address_cache` list guarded by `rpcbaddr_cache_lock`. `local_rpcb()` caches a selected loopback `netconfig` and loopback hostname under `loopnconf_lock`. Timeouts are global (`tottimeout`, `rpcbrmttime`) and can be changed through `__rpc_control`; `__rpc_lowvers` is also controlled there.

Dependencies and integration points: relies on `rpc_generic.c` address conversion, local rpcbind Unix socket paths, GSS-independent RPC client calls, netconfig, `rpcb_prot.c` XDR, optional portmapper compatibility, and debug logging. Service registration from `svc.c` and service creation from `svc_generic.c` call `rpcb_set`/`rpcb_unset`.

Risks: global cache and timeout changes affect all threads. Cache deletion compares raw netbuf bytes and may evict any matching address regardless of host/netid. `local_rpcb()` never frees the cached netconfig. Fallback order changes under `RPCB_V2FIRST`. Some error paths depend on `rpc_createerr` global state.

Test signals: local abstract and pathname rpcbind sockets, remote `getaddrinfo` resolution, cache hit/miss/delete behavior under concurrent lookups, v4-to-v3 fallback, portmap v2 fallback for IPv4, `RPCB_V2FIRST`, `rpcb_set`/`rpcb_unset` owner strings, address-too-small failure in `rpcb_getaddr`, rmtcall result address copying, and timeout control through `__rpc_control`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libtirpc/src/rpcb_clnt.c -->
