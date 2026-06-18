# sources/user-network-fs/samba/source4/torture/rpc/async_bind.c

## Purpose
`async_bind.c` tests concurrent asynchronous DCE/RPC bind setup. It sends multiple LSARPC pipe connect requests before receiving any of them, then verifies that each bind completes successfully.

## Important APIs, types, and functions
The exported function is `torture_async_bind()`. It uses `dcerpc_pipe_connect_send()`, `dcerpc_pipe_connect_recv()`, `samba_cmdline_get_creds()`, generated `ndr_table_lsarpc`, the torture `binding` setting, and external `torture_numasync` for request count. Request state is stored in arrays of `struct composite_context *`, `struct dcerpc_pipe *`, and `const struct ndr_interface_table *`.

## Control flow
The test is disabled unless the `async` torture setting is true. When enabled, it reads the binding string, creates a temporary talloc context, allocates arrays sized by `torture_numasync`, obtains command-line credentials, and loops once to send every LSARPC async connect. A second loop receives each connection result and fails immediately if any status is not OK. On success it frees the temporary context and returns true.

## State and persistence behavior
State is client-side only: outstanding composite contexts and connected pipe objects owned by the temporary talloc context. No remote objects are created beyond transient RPC associations and binds. The test intentionally overlaps bind operations on the same event context.

## Dependencies and integration points
It depends on the composite async RPC API, event loop in the torture context, command-line credentials, and generated LSARPC NDR metadata. It is an integration test for transport connection setup, bind sequencing, and event-driven completion.

## Risks and edge cases
Allocation failures return false without freeing earlier allocations. The test assumes the same binding string is valid for all concurrent binds and does not throttle request count. Disabled-by-default behavior means it gives no coverage unless explicitly configured. If one receive fails, already connected pipes are left to context cleanup.

## Test signals
The primary signal is all `torture_numasync` `dcerpc_pipe_connect_recv()` calls returning OK. Failures indicate async transport, event-loop, server bind fanout, or authentication scalability problems.
