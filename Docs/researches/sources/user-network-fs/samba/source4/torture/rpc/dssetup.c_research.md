# sources/user-network-fs/samba/source4/torture/rpc/dssetup.c

## Purpose
`dssetup.c` is a compact torture suite for the DSSETUP RPC interface. It tests `DsRoleGetPrimaryDomainInformation` across all defined info levels from basic information through operation status.

## Important APIs, types, and functions
`test_DsRoleGetPrimaryDomainInformation_ext` is the reusable helper that accepts an expected transport `NTSTATUS`; `test_DsRoleGetPrimaryDomainInformation` calls it expecting `NT_STATUS_OK`. `torture_rpc_dssetup` registers the test against `ndr_table_dssetup`. It uses generated `dcerpc_dssetup_DsRoleGetPrimaryDomainInformation_r` and torture assertions.

## Control flow
The suite creates one RPC tcase named `dssetup`. The test loops from `DS_ROLE_BASIC_INFORMATION` through `DS_ROLE_OP_STATUS`, sets `r.in.level`, calls the generated RPC stub, asserts the transport status equals the expected status, and when that expected status is OK asserts `r.out.result` is `WERR_OK`.

## State and persistence behavior
The module is read-only. It does not allocate persistent server state, alter domain role information, or maintain fixture-private state beyond the stack request structure.

## Dependencies and integration points
It depends on generated DSSETUP NDR client bindings and Samba torture RPC framework. The exported suite builder is the integration point used by the broader torture runner.

## Risks and edge cases
The loop assumes every level in the contiguous enum range is valid and expected to succeed when the transport does. If future enum values are inserted or a server intentionally restricts a level, this simple range loop may over-assert. The `_ext` helper allows other tests to reuse the same loop for expected transport failures.

## Test signals
Pass is simple: every level returns the expected NTSTATUS, and successful transport includes `WERR_OK`. Torture comments include the level number being tested, which is useful for pinpointing failures.
