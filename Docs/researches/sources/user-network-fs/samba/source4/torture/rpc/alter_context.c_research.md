# sources/user-network-fs/samba/source4/torture/rpc/alter_context.c

## Purpose
`alter_context.c` tests DCE/RPC alter-context behavior. It checks that a pipe can alter its existing presentation context, create a secondary context for another interface, reject an unsupported interface version, and preserve or fault operations according to the active abstract syntax.

## Important APIs, types, and functions
The exported test is `torture_rpc_alter_context()`. It uses `dcerpc_alter_context()`, `dcerpc_secondary_context()`, `dcerpc_binding_handle_get_binding()`, `dcerpc_binding_get_abstract_syntax()`, `dcerpc_binding_get_flags()`, `test_lsa_OpenPolicy2()`, `test_lsa_OpenPolicy2_ex()`, `test_lsa_Close()`, `test_DsRoleGetPrimaryDomainInformation()`, and `test_DsRoleGetPrimaryDomainInformation_ext()`. Interfaces involved are `ndr_table_lsarpc` and `ndr_table_dssetup`.

## Control flow
The test opens an LSARPC connection, extracts its abstract syntax and transfer syntax (`NDR` or `NDR64`), and alters the primary context back to that syntax. It verifies LSA open/close still works, opens a DSSETUP secondary context, alters that context, then attempts a bad secondary context with a deliberately invalid DSSETUP version and expects `RPC_UNSUPPORTED_NAME_SYNTAX`. It then alternates LSA and DSSETUP calls through the primary and secondary pipes. Finally it attempts to alter the primary LSA pipe to DSSETUP syntax; some servers disconnect with protocol error, while others accept the context but DSSETUP calls on the original binding should fault with bad stub data before LSA is verified again.

## State and persistence behavior
The state is DCE/RPC connection state: presentation contexts, association state, binding handles, and policy handles opened and closed during the test. It persists no server data. A protocol-error path may intentionally disconnect the binding handle and ends the test early after checking disconnected state.

## Dependencies and integration points
The file depends on generated NDR tables for LSA and DSSETUP, generic RPC torture helpers, DCE/RPC binding syntax metadata, and transport support for alter-context PDUs. It integrates with LSA and DSSETUP test helper functions from the broader torture RPC suite.

## Risks and edge cases
Expected behavior differs by server when an existing context is altered to a different abstract syntax. The test must preserve transfer syntax choice when NDR64 is negotiated. Policy handles must be closed only when opened. The bad-version test depends on the NDR table copy being modified without corrupting the original global table.

## Test signals
Signals include successful repeated alter-context calls on valid syntax, successful LSA operations after altering, successful DSSETUP operations through a secondary context, `RPC_UNSUPPORTED_NAME_SYNTAX` for a bad secondary version, and either clean protocol disconnect or `RPC_BAD_STUB_DATA` for intentionally mismatched primary-context calls.
