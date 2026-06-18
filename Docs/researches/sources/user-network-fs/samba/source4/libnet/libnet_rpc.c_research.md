# sources/user-network-fs/samba/source4/libnet/libnet_rpc.c

## Purpose

`libnet_rpc.c` provides libnet's asynchronous and synchronous DCERPC connection factory. It turns a `libnet_RpcConnect` request into an authenticated `dcerpc_pipe`, optionally resolving a DC/PDC, querying domain metadata through LSA, and deriving a secondary connection to the requested interface through endpoint mapping.

## Important APIs, Types, and Functions

Public APIs are `libnet_RpcConnect_send()`, `libnet_RpcConnect_recv()`, and synchronous `libnet_RpcConnect()`.

Internal state machines:
- Server path: `libnet_RpcConnectSrv_send()`, `continue_pipe_connect()`, `libnet_RpcConnectSrv_recv()`.
- DC/PDC path: `libnet_RpcConnectDC_send()`, `continue_lookup_dc()`, `continue_rpc_connect()`, `libnet_RpcConnectDC_recv()`.
- DC-info path: `libnet_RpcConnectDCInfo_send()`, `continue_dci_rpc_connect()`, `continue_lsa_policy()`, `continue_lsa_query_info2()`, `continue_lsa_query_info()`, `continue_epm_map_binding_send()`, `continue_epm_map_binding()`, `continue_secondary_conn()`, `libnet_RpcConnectDCInfo_recv()`.

The code also emits monitor messages for lookup, RPC connect, LSA policy open, and LSA policy query progress.

## Control Flow

Direct server/binding flow builds or parses a binding string, applies caller flags and debug flags, calls `dcerpc_pipe_connect_b_send()`, and returns the resulting pipe. Server-address requests use `ncacn_np:<address>[target_hostname=<name>]` to preserve the target host identity while connecting to an address.

DC/PDC flow first calls `libnet_LookupDCs_send()` with `NBT_NAME_LOGON` or `NBT_NAME_PDC`, then connects to the first returned DC via the server-address path.

DC-info flow connects to LSARPC first, opens policy over named pipe transports, queries DNS-domain/GUID and NetBIOS-domain/SID policy info when available, maps the requested RPC interface with EPM using anonymous credentials, then creates a secondary authenticated connection from the LSA pipe. TCP transports skip LSA policy open and go directly to endpoint mapping because policy open is not supported there.

## State and Persistence Behavior

Connection results are talloc-moved or reparented into the caller's memory context. For SAMR and LSARPC interfaces, the returned pipe and binding handle are also referenced into the long-lived `libnet_context` caches (`ctx->samr` or `ctx->lsa`) so later libnet operations can reuse handles after the short-lived call context is freed. DC-info output may include domain name, domain SID, realm, and GUID.

## Dependencies and Integration Points

The file integrates with Samba composite async primitives, tevent requests, `dcerpc_pipe_connect_b`, endpoint mapper helpers, secondary-auth connection helpers, generated LSA/SAMR interface tables, `libnet_LookupDCs`, credentials, and monitor-message infrastructure. It is foundational for password, share, time, domain-open, join, and user management code.

## Risks and Edge Cases

The DC-info monitor block in `continue_dci_rpc_connect()` dereferences `s->r.out.dcerpc_pipe` even though the just-opened pipe is stored in `s->rpc_conn`/context LSA state; this path deserves scrutiny if monitor callbacks are enabled. Memory ownership is delicate: one path uses `talloc_reparent()` with comments noting poor historical talloc usage. `libnet_RpcConnect_recv()` handles `LIBNET_RPC_CONNECT_SERVER_ADDRESS` in send but not explicitly in recv, which is a potential mismatch to test. LSA policy info may legitimately be unavailable on non-AD or unsupported transports, so callers must tolerate NULL realm/GUID/domain outputs.

## Test Signals

`source4/torture/libnet/libnet_rpc.c` is the primary signal, covering server, PDC, DC, DC-info, and binding levels. Additional signals come indirectly from all SAMR/SRVSVC/LSA users. Tests should assert returned pipe ownership, cached context handles, DC-info metadata, monitor callbacks, binding flags, debug flag behavior, endpoint mapper failures, and server-address recv behavior.
