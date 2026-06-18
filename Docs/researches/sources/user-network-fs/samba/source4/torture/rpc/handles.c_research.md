# sources/user-network-fs/samba/source4/torture/rpc/handles.c

## Purpose
This file implements the `rpc.handles` suite for DCE/RPC context-handle behavior. It checks whether LSA, SAMR, and DRSUAPI policy handles are scoped to a connection, shared across an association group, invalid across interfaces, and invalid after closure or association teardown.

## Important APIs, Types, And Functions
`torture_rpc_handles()` registers simple tests for `lsarpc`, `lsarpc-shared`, `samr`, `mixed-shared`, `random-assoc`, and `drsuapi`. Tests use `torture_rpc_connection()`, `torture_rpc_connection_transport()`, `dcerpc_binding_get_assoc_group_id()`, `dcerpc_binding_get_transport()`, LSA `OpenPolicy/QuerySecurity/Close`, SAMR `Connect/Close`, and DRSUAPI `DsBind/DsUnbind`.

## Control Flow
Simple LSA/SAMR/DRSUAPI tests open a handle on one pipe, try to close it on another pipe and expect `NT_STATUS_RPC_SS_CONTEXT_MISMATCH`, close it on the original pipe, then verify a second close faults. Shared LSA tests create additional pipes in the same association group before and after opening a handle, verify the handle works across those pipes, close from one pipe, then verify all others fault. They also test that a handle survives disconnect of the original pipe while other group members remain, but that creating another pipe after all group members are gone fails. Mixed-shared tests verify SAMR handles cannot be consumed through LSARPC even in the same association group, then probe failure for stale or random association IDs.

## State And Persistence Behavior
The file creates transient RPC connections and server-side context handles. It does not persist directory or registry state. Its stateful behavior is association-group lifetime: freeing pipes is part of the test and is followed by short sleeps so the server observes disconnects.

## Dependencies And Integration Points
The suite depends on generated LSA, SAMR, and DRSUAPI NDR clients and the torture RPC transport helper that can force a transport and association group ID. It integrates with low-level RPC runtime behavior rather than high-level service data.

## Risks And Edge Cases
Several expected failures are transport/runtime-specific, especially `NT_STATUS_UNSUCCESSFUL` when reusing expired or random association groups. The shared LSA test has two assertions that compare a stale `status` variable after `QuerySecurity` calls rather than `qsec.out.result`; this could mask a bad result even when the RPC transport status is OK. Timing sleeps are small and may expose races in slow environments.

## Test Signals
Primary signals are exact context-mismatch faults on cross-pipe or double-close attempts, successful shared-handle use within a live association group, `NT_STATUS_UNSUCCESSFUL` for stale/random group connection attempts, and skip behavior for unsupported `OpenPolicy` or `DsBind`.
