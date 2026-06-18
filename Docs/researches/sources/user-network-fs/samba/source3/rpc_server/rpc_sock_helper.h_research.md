# sources/user-network-fs/samba/source3/rpc_server/rpc_sock_helper.h

## Purpose
This header exposes the socket creation helper used by the RPC host to turn a DCE/RPC binding into one or more listening file descriptors.

## Important APIs, Types, And Functions
It includes `rpc_server.h` and declares `dcesrv_create_binding_sockets(struct dcerpc_binding *b, TALLOC_CTX *mem_ctx, size_t *pnum_fds, int **fds)`.

## Control Flow
The header has no runtime flow. Its function contract returns a talloc-owned fd array and count, with the binding potentially updated by the implementation for dynamic endpoint selection.

## State And Persistence
No state is declared. Callers own returned fds and must close them when endpoint state is destroyed.

## Dependencies And Integration Points
The declaration is consumed by `rpc_host.c` during server setup and implemented by `rpc_sock_helper.c`.

## Risks And Test Signals
Risks are caller assumptions about single-fd endpoints and missing awareness that TCP can return multiple fds. Test signals are compile coverage and endpoint setup tests for all supported transports.
