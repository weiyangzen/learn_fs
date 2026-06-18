# sources/user-network-fs/samba/source3/rpc_client/rpc_transport.h

## Purpose
`rpc_transport.h` defines the asynchronous transport abstraction used by source3 RPC clients to move DCE/RPC PDUs over sockets, SMB named pipes, or generic tstreams.

## Important APIs, Types, And Functions
The core type is `struct rpc_cli_transport`, with transport kind, async `read_send/read_recv`, `write_send/write_recv`, optional transact-style `trans_send/trans_recv`, connection check, timeout setter, and private state pointer. It declares constructors `rpc_transport_np_init_send/recv()`, `rpc_transport_sock_init()`, `rpc_transport_tstream_init()`, and accessor `rpc_transport_get_tstream()`.

## Control Flow
No runtime logic is in the header. The abstraction lets `cli_pipe.c` issue reads/writes or use the optional named-pipe transact optimization when available.

## State And Persistence
The struct holds runtime transport state and callbacks only. Persistence is outside this layer.

## Dependencies And Integration Points
It depends on `librpc/rpc/dcerpc.h`, `cli_state`, tevent, and tstream types. Implementations are `rpc_transport_np.c`, `rpc_transport_sock.c`, and `rpc_transport_tstream.c`; consumers include RPC bind/call code and WSP/mdssvc clients.

## Risks
Callback contracts allow short reads/writes, so callers must handle fragmentation. `trans_send` is optional, and fallback paths must remain tested. Timeout semantics can differ by concrete transport.

## Test Signals
Transport tests should exercise read/write over socket and named pipe, optional transact use over SMB named pipes, timeout changes, disconnection detection, short I/O handling, and constructor failure cleanup.
