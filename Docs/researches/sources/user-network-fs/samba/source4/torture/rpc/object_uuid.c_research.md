# sources/user-network-fs/samba/source4/torture/rpc/object_uuid.c

## Purpose

`object_uuid.c` tests whether DCERPC requests carrying arbitrary object UUIDs are accepted for selected RPC interfaces. It verifies that Samba's DCERPC client path can pass a non-null object UUID through `dcerpc_binding_handle_call()` without breaking normal server dispatch for DS setup and LSA calls.

## Important APIs, Types, and Functions

The only test body is `test_random_uuid()`. It opens two RPC pipes, one to `ndr_table_dssetup` and one to `ndr_table_lsarpc`, generates random GUIDs with `GUID_random()`, and calls:

- `NDR_DSSETUP_DSROLEGETPRIMARYDOMAININFORMATION` with `dssetup_DsRoleGetPrimaryDomainInformation`.
- `NDR_LSA_GETUSERNAME` with `lsa_GetUserName`.

The suite factory `torture_rpc_object_uuid()` registers this as `random-uuid`.

## Control Flow

The test opens the DS setup pipe, opens the LSA pipe, generates a random object UUID, calls DS role information through the generic binding-handle call API, asserts transport success and WERROR success, generates another random UUID, then calls LSA `GetUserName` and asserts transport and operation NTSTATUS success.

The test deliberately uses `dcerpc_binding_handle_call()` instead of the generated convenience wrappers so it can pass the object UUID parameter explicitly.

## State and Persistence Behavior

The test is read-only. It creates transient pipe handles, local GUIDs, request structures, and output string pointers. It does not mutate server state or retain any process-global state.

## Dependencies and Integration Points

The file depends on generated NDR metadata for DS setup and LSA, the Samba torture RPC connection helper, GUID generation, and the generic DCERPC binding-handle call path. It integrates into the torture suite namespace as `objectuuid`.

## Risks and Edge Cases

The test assumes the target accepts arbitrary object UUIDs for these calls. A server or transport that enforces object UUID filtering more strictly could fail even if the operations themselves work through generated wrappers.

The failure messages for the LSA call say `"lsaClose failed"` even though the operation is `GetUserName`; this is only diagnostic text but can make failure triage less direct.

## Test Signals

Success is transport-level `NT_STATUS_OK` plus operation-level success for both DS setup and LSA calls while a random object UUID is present. This signals that object UUID marshalling and dispatch interaction are functioning for the tested interfaces.
