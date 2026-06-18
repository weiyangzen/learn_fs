# sources/user-network-fs/libtirpc/tirpc/rpc/rpcb_clnt.h

Purpose: `rpcb_clnt.h` declares transport-independent rpcbind client routines for registering, unregistering, resolving, dumping, remote-calling, time querying, and address conversion.

Important APIs, types, and functions: APIs include `rpcb_set`, `rpcb_unset`, `rpcb_getmaps`, `rpcb_rmtcall`, `rpcb_getaddr`, `rpcb_gettime`, `rpcb_taddr2uaddr`, and `rpcb_uaddr2taddr`.

Control flow: Callers pass program/version and `netconfig` data to register or resolve universal addresses in rpcbind. Remote calls encode supplied args/results through XDR callbacks and may return an address. Address conversion bridges `struct netbuf` and universal address strings.

State and persistence behavior: Persistent mappings live in rpcbind, not the client library. Returned maps/addresses/netbufs are allocated by implementation and must be freed according to API conventions.

Dependencies and integration points: It depends on `rpcb_prot.h`, `rpc/types.h`, and netconfig/netbuf definitions. Generic `clnt_create` and `svc_register` code uses rpcbind client helpers.

Risks: `rpcb_rmtcall` takes `const caddr_t` for result storage, reflecting historical prototypes and requiring careful casts. Network failures and quiet remote-call semantics can obscure missing services. Memory ownership of returned universal addresses and map lists must be clear to callers.

Test signals: Tests should cover set/unset/getaddr against local rpcbind, map dump/free, time query, taddr/uaddr round trips, remote call success/failure, and IPv4/IPv6 netconfig variants.
