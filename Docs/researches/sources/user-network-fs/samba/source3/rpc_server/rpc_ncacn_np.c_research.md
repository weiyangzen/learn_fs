# sources/user-network-fs/samba/source3/rpc_server/rpc_ncacn_np.c

## Purpose
This file provides local named-pipe style RPC client helpers for source3 RPC servers. It creates queue state for named-pipe authentication streams and opens local RPC client connections that dispatch directly to Samba's local named-pipe implementation instead of connecting over a remote network transport.

## Important APIs, Types, And Functions
`struct np_proxy_state` is a private proxy-shape state for pipe metadata and tevent queues. The public `npa_state_init` allocates `struct npa_state` and initializes separate read and write queues. `rpcint_binding_handle` opens a local named-pipe RPC client for a specific NDR interface table and returns its `dcerpc_binding_handle`. `rpc_pipe_open_interface` opens or reuses a `struct rpc_pipe_client` for a given interface table, session info, and remote/local address pair.

## Control Flow
`npa_state_init` is a simple allocation path with cleanup on queue allocation failure. `rpcint_binding_handle` calls `rpc_pipe_open_local_np`, using the provided session and address context, and moves the resulting binding handle out of the `rpc_pipe_client`. `rpc_pipe_open_interface` first checks whether an existing caller-supplied pipe is still connected. If not, it frees it, opens a new local named-pipe client with `rpc_pipe_open_local_np`, stores it back through `cli_pipe`, and reports errors with the interface table name.

## State And Persistence
There is no durable persistence. State is talloc-owned queue and pipe-client state. `rpc_pipe_open_interface` may preserve a live caller-owned `rpc_pipe_client` across calls, so the caller controls connection caching and lifetime.

## Dependencies And Integration Points
The code depends on `rpc_client/cli_pipe.h`, `rpc_dce.h`, `named_pipe_auth`, `auth_session_info`, `tsocket_address`, `rpc_pipes.h`, and `rpc_server.h`. It is the internal bridge used by RPC services that need to call another local RPC interface such as winreg, samr, or netlogon without routing through an external network client.

## Risks And Test Signals
Risks include stale cached clients, address/session mismatches when services reuse `cli_pipe`, and returning `rpccli->binding_handle` while freeing the containing client only on failure. Test signals are local interface open/reopen behavior, disconnected cached pipe replacement, session propagation, and service-to-service RPC calls made from inside worker processes.
