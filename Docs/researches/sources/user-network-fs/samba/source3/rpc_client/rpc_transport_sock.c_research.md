# sources/user-network-fs/samba/source3/rpc_client/rpc_transport_sock.c

## Purpose
`rpc_transport_sock.c` adapts an existing socket file descriptor into the common RPC transport abstraction.

## Important APIs, Types, And Functions
The single export is `rpc_transport_sock_init(TALLOC_CTX *mem_ctx, int fd, struct rpc_cli_transport **presult)`. It uses `set_blocking(fd, false)`, `tstream_bsd_existing_socket()`, and `rpc_transport_tstream_init()`.

## Control Flow
The function marks the fd nonblocking, wraps it as a BSD `tstream_context`, then delegates to the tstream transport initializer. On tstream transport initialization failure it frees the intermediate stream and returns the NTSTATUS error.

## State And Persistence
No persistent state exists. Ownership of the fd moves into the tstream on success, and then into the RPC transport state.

## Dependencies And Integration Points
It depends on tsocket/tstream support and `rpc_transport_tstream.c`. It is used wherever source3 RPC clients already have a connected socket rather than an SMB named pipe.

## Risks
`set_blocking()` return is not checked, so a failure to mark nonblocking may only appear later as I/O behavior. Callers must pass a valid connected fd and must not close it after successful initialization. Transact optimization is unavailable for plain sockets because the tstream transport only enables it for SMB named-pipe streams.

## Test Signals
Socketpair-based tests should verify successful initialization, nonblocking I/O, failed wrapping on invalid fds, cleanup on `rpc_transport_tstream_init()` failure, and read/write behavior through the common transport.
