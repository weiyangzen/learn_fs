# sources/user-network-fs/samba/source3/rpc_server/rpc_server.h

## Purpose
`rpc_server.h` declares the common ncacn connection wrapper and shared source3 DCE/RPC server hooks. It is included by worker, socket, named-pipe, and service code that needs transport-private state or common callbacks.

## Important APIs, Types, And Functions
`dcerpc_ncacn_termination_fn` defines termination callbacks. `struct dcerpc_ncacn_conn` links active connections, stores the socket, embedded `pipes_struct`, endpoint, termination callback, client/server names and addresses, and connection timestamp. The header declares fault/PDU helpers, auth callbacks, association group lookup, endpoint lookup, pipe-struct extraction, and transport termination.

## Control Flow
The declarations support bind and packet flow in dcesrv: a transport creates `dcerpc_ncacn_conn`, embeds it as `dcesrv_connection->transport.private_data`, uses callbacks for auth and association groups, and calls termination when the dcesrv connection is freed.

## State And Persistence
All declared state is in-memory connection or association state. No persistent data is owned by this header.

## Dependencies And Integration Points
It depends on common RPC definitions, `dcesrv_core`, `rpc_pipes.h`, and basic time types. It is used by `rpc_worker.c`, `rpc_server.c`, `rpc_sock_helper.c`, and internal service implementations.

## Risks And Test Signals
Risks are ABI and ownership coupling: every transport-private pointer must really be a `dcerpc_ncacn_conn`, and the embedded `pipes_struct` must match expectations of source3 RPC stubs. Test signals are compile coverage, connection create/free cycles, and callback invocation during forced disconnects.
