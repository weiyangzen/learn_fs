# sources/user-network-fs/samba/source3/rpc_client/rpc_client.h

## Purpose
`rpc_client.h` defines the source3 RPC pipe client object shape and internal/external visibility boundary for RPC client internals.

## Important APIs, Types, And Functions
The central type is `struct rpc_pipe_client`, with list links, printer username, destination host, slash server name, public `dcerpc_binding_handle`, and conditionally hidden internals. Internals include named-pipe `cli_state`, association/connection pointers, auth data, presentation context id, interface table, transfer syntax, and verified-pcontext flag. Macros `SOURCE3_LIBRPC_INTERNALS_BEGIN/END` hide internals unless `SOURCE3_LIBRPC_INTERNALS` is defined.

## Control Flow
The header has no runtime control flow. It controls compile-time access to structure fields and includes RPC/ndr/transport definitions needed by client implementations.

## State And Persistence
`rpc_pipe_client` is runtime connection state only. It tracks RPC association, binding, authentication, selected NDR interface, and transport linkage; it does not persist to disk.

## Dependencies And Integration Points
It depends on generated DCE/RPC types, `librpc/rpc/dcerpc.h`, NDR helpers, and `rpc_transport.h`. It is integrated with `cli_pipe.c`, pipe authentication, named-pipe transports, and higher-level RPC client commands.

## Risks
The conditional field-hiding pattern means code compiled without internals should not depend on layout. Any change to `rpc_pipe_client` internals can affect source3 RPC connection setup, authentication, and presentation-context verification.

## Test Signals
Compile coverage across internal and external users is key. Runtime signals are successful RPC bind/auth/call paths over all supported transports and tests that exercise printer-specific username/destination fields.
