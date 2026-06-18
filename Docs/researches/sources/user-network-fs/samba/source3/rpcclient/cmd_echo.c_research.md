# sources/user-network-fs/samba/source3/rpcclient/cmd_echo.c

## Purpose
`cmd_echo.c` implements rpcclient commands for the test ECHO RPC interface. It is primarily a transport, marshalling, and server sanity-check tool.

## Important APIs, types, and functions
- `cmd_echo_add_one()` calls `dcerpc_echo_AddOne()` and prints the arithmetic result.
- `cmd_echo_data()` allocates input/output buffers, fills deterministic byte data, calls `EchoData`, and verifies round-trip equality.
- `cmd_echo_source_data()` calls `SourceData` and validates that the server produced the expected byte pattern.
- `cmd_echo_sink_data()` fills a buffer and sends it to `SinkData`.
- `echo_commands[]` registers `echoaddone`, `echodata`, `sinkdata`, and `sourcedata` as `RPC_RTYPE_NTSTATUS` against `ndr_table_rpcecho`.

## Control flow
Each command validates simple argument counts, parses optional sizes with `atoi`, allocates buffers with `SMB_MALLOC`, fills or checks byte patterns, invokes the generated ECHO stub, and frees buffers with `SAFE_FREE` on all exit paths.

## State and persistence behavior
All commands are stateless test calls. They allocate transient process memory and do not mutate persistent server state.

## Dependencies and integration points
The module depends on rpcclient command registration, generated rpcecho client stubs, Samba memory macros, and the server-side `RPC_RPCECHO` subsystem/build target used in selftests.

## Risks and edge cases
- Size parsing uses `atoi` into `uint32_t`; negative or very large input can become large allocations or wrap.
- Zero-size allocation behavior depends on `SMB_MALLOC`.
- The commands return `NT_STATUS_OK` for usage errors, which is common for rpcclient help behavior but weak for automation.

## Test signals
Run the commands against `rpcd_rpcecho` with zero, small, and moderate buffer sizes. Negative tests should include malformed size strings and unreachable echo service bindings.
