# sources/user-network-fs/samba/source4/torture/rpc/countcalls.c

## Purpose
`countcalls.c` is a diagnostic torture helper that estimates how many opnums an RPC interface accepts before returning an out-of-range or disconnect-style status. It can target one configured interface or iterate every registered NDR interface.

## Important APIs, types, and functions
`count_calls()` opens an RPC pipe for a supplied `struct ndr_interface_table`, then invokes `dcerpc_binding_handle_raw_call()` with empty input stubs for opnums `0..499`. `torture_rpc_countcalls()` reads the optional `countcalls:interface` loadparm setting, resolves it with `ndr_table_by_name()`, or walks `ndr_table_list()`. It uses `DATA_BLOB`, `talloc_named()` loop contexts, `torture_rpc_connection()`, and NTSTATUS helpers.

## Control flow
For a single interface, the runner resolves and scans just that interface; unknown names are fatal. For all interfaces, it creates a short-lived talloc context per interface, calls `count_calls(..., all=true)`, and accumulates a boolean result. Inside `count_calls`, connection failures that commonly mean the pipe is absent, inaccessible, or not listening are non-fatal only in all-interface mode. Once connected, the loop stops on `NT_STATUS_RPC_PROCNUM_OUT_OF_RANGE`, disconnects, access denial, or logon failure; the final accepted count is printed. Reaching 500 without a stop status is treated as suspicious failure.

## State and persistence behavior
The module has no persistent state and sends no meaningful request payloads. It may still affect remote logs or connection counters because it sends raw calls to many opnums. It frees each pipe and per-interface context after scanning.

## Dependencies and integration points
It depends on Samba's global NDR table registry, torture RPC connection helpers, and the target server's endpoint availability. It integrates as `bool torture_rpc_countcalls(struct torture_context *torture)`, not as a standard `struct torture_suite` builder.

## Risks and edge cases
Raw empty calls can produce server-side faults, disconnects, or audit noise, especially against interfaces that treat early opnums as state-changing or require non-empty stubs. The count is approximate because access control, authentication failure, or pipe disconnect can end the scan before the true procnum limit. The hard upper bound of 500 is an arbitrary sanity cap.

## Test signals
Useful output is textual: "Scanning pipe" and "Found N calls". Failure signals include unknown interface names, unexpected connection failures for an explicitly requested interface, or no terminating status before 500 opnums.
