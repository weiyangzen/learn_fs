# sources/user-network-fs/nfs-utils/support/nfs/getport.c

Purpose: RPC service discovery helpers for querying local or remote rpcbind/portmapper and verifying service responsiveness.

Important APIs: `nfs_get_proto()`, `nfs_get_netid()`, `nfs_universal2port()`, `nfs_sockaddr2universal()`, `nfs_rpc_ping()`, `nfs_getport()`, `nfs_getport_ping()`, `nfs_getlocalport()`, `nfs_rpcb_getaddr()`, `nfs_pmap_getport()`, and `nfs_probe_statd()`.

Control flow: rpcbind clients are created with `nfs_gp_get_rpcbclient()`, which discovers the rpcbind port from `/etc/services` names or `PMAPPORT`. IPv4 lookups use pmap v2 `PMAPPROC_GETPORT`; IPv6 with TI-RPC uses rpcbind v4 then v3 `RPCBPROC_GETADDR` on the same client. Universal addresses are built from sockaddr plus high/low port components and parsed back by stripping the last two dotted decimal fields. Ping variants set the discovered port and issue an RPC `NULLPROC`.

State and persistence: no durable state. It mutates `rpc_createerr` as the error side channel and may update caller sockaddr ports in `nfs_getport_ping()`. Service-name lookups read system databases such as `/etc/services`, `/etc/rpc`, `/etc/netconfig`, DNS/NSS, and rpcbind state.

Dependencies and integration: depends on TI-RPC when available, legacy SunRPC otherwise, `sockaddr.h`, `nfsrpc.h`, and `nfslib.h`. It integrates with mount/statd probing and service discovery code.

Risks: default timeout uses `tv_sec = -1` as a sentinel interpreted by client creation helpers, so callers must pass initialized timevals. `nfs_sockaddr2universal()` uses `sizeof(struct sockaddr)` to derive AF_LOCAL path length, which is suspicious for longer `sockaddr_un` values. Global `rpc_createerr` makes the APIs non-thread-local. Behavior differs for libtirpc vs non-libtirpc, especially IPv6 and netid support.

Test signals: IPv4 pmap success/failure, IPv6 rpcbind v4 fallback to v3, malformed universal addresses, services database overrides, TCP timeout/refused error mapping, local rpcbind fallback, statd probing, and non-libtirpc unsupported address cases.
