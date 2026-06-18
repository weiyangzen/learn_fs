## sources/user-network-fs/libtirpc/src/pmap_getport.c

Purpose: Implements `pmap_getport`, querying a host's legacy portmapper for a program/version/protocol port.

Important APIs and control flow: The function sets the target IPv4 address port to `PMAPPORT`, creates a UDP client with small buffers and a 5-second retry timeout, sends `PMAPPROC_GETPORT` with an `xdr_pmap` argument and `xdr_u_short` result under a 60-second total timeout, records `RPC_PMAPFAILURE` plus nested client error on RPC failure, records `RPC_PROGNOTREGISTERED` for a zero result, destroys the client, restores address port to zero, and returns the port.

State and persistence: No local persistent state; it updates global/thread `rpc_createerr` on failure.

Dependencies and integration: Used by `getrpcport` and older RPC clients. Depends on UDP client compatibility and pmap XDR.

Risks and test signals: IPv4/UDP only and mutates input sockaddr. Tests should cover success, zero-port unregistered, RPC transport failure, client creation failure, timeout constants, and port restoration.
