# sources/user-network-fs/samba/source3/rpc_server/rpc_ncacn_np.h

## Purpose
This header exposes the local named-pipe RPC helper surface used by source3 RPC server code. It declares named-pipe auth stream state and functions for creating local RPC binding handles or pipe clients.

## Important APIs, Types, And Functions
`struct npa_state` stores the backing `tstream_context`, read/write `tevent_queue`s, pipe allocation size, device state, file type, and caller-private data. `npa_state_init` allocates that state. `rpcint_binding_handle` returns a `dcerpc_binding_handle` for an NDR interface. `rpc_pipe_open_interface` returns or refreshes a `struct rpc_pipe_client`.

## Control Flow
The header itself has no runtime flow, but its contracts imply talloc ownership: callers pass a memory context and receive objects owned under that context or the returned pipe client.

## State And Persistence
No persistent state is declared. Runtime state is per-pipe and is intended to be owned by the caller's talloc tree.

## Dependencies And Integration Points
It forward-declares DCE/RPC, NDR, tsocket, and endpoint structures so service code can include it without pulling in full implementation headers. It is paired with `rpc_ncacn_np.c` and integrates with local `rpc_pipe_open_local_np` dispatch.

## Risks And Test Signals
Risk is mostly ownership and incomplete-type coupling. Test signals are compile coverage for callers using only forward declarations, local pipe creation, and teardown of read/write queues.
