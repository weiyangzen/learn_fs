# sources/user-network-fs/libtirpc/tirpc/rpc/rpc.h

Purpose: `rpc.h` is the umbrella public include for TI-RPC, aggregating base types, XDR, auth, client, server, RPC message, portmapper, rpcbind, multithreaded service, and rpc database APIs.

Important APIs, types, and functions: Besides includes, it defines fallback `UDPMSGSIZE` and declares legacy helpers `get_myaddress`, `bindresvport`, `registerrpc`, `callrpc`, `getrpcport`, address converters `taddr2uaddr`/`uaddr2taddr`, `bindresvport_sa`, and internal library/rpcbind helpers like `__rpc_nconf2fd`, `__rpc_nconf2sockinfo`, `__rpc_fd2sockinfo`, and `__rpc_get_t_size`.

Control flow: Consumers include this header to access most RPC APIs. High-level helpers perform one-shot registration/calls, reserved-port binding, and transport address conversion. Internal helpers map netconfig/socket descriptors to fd and socket metadata for client/server creation.

State and persistence behavior: The header declares no storage. Included subheaders expose stateful client, server, auth, and rpcbind APIs.

Dependencies and integration points: It pulls in nearly every public libtirpc component and must maintain include ordering for types such as `netbuf`, `CLIENT`, `SVCXPRT`, and XDR.

Risks: Umbrella includes can create circular dependency sensitivity; this file includes both public and internal helpers, with comments warning internal functions may change. Including AUTH_DES by default exposes obsolete DES interfaces. Legacy helper prototypes use old integer types.

Test signals: Tests should compile representative legacy and modern consumers with only `<rpc/rpc.h>`, verify no include-order breakage, and exercise one-shot `callrpc`/`registerrpc` plus address conversion helpers.
