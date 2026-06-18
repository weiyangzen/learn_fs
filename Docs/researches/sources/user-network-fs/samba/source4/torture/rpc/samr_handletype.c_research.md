# sources/user-network-fs/samba/source4/torture/rpc/samr_handletype.c

## Purpose

This file defines the `samr.handletype` torture suite, focused on validating SAMR policy-handle context typing. It checks that operations fail with `NT_STATUS_RPC_SS_CONTEXT_MISMATCH` when a policy handle has the right wire shape but either a tampered context UUID or an incorrect `handle_type` field.

## Important APIs, Types, and Functions

- `enum samr_handle` mirrors the SAMR handle-type values used by the test: connect, domain, user, group, and alias.
- `torture_samr_Close()` wraps `dcerpc_samr_Close_r()`.
- `torture_samr_Connect5()` opens a SAMR connect handle for a requested mask.
- `test_samr_handletype_OpenDomain()` is the only test body. It exercises `LookupDomain`, `OpenDomain`, `OpenUser`, and `OpenGroup` with both valid and deliberately corrupted handles.
- `torture_rpc_samr_handletype()` registers the suite and an RPC tcase for `ndr_table_samr`.

## Control Flow

The test first connects with `SEC_FLAG_MAXIMUM_ALLOWED`, looks up the configured workgroup domain SID, and then reconnects with a minimal access mask. It copies the valid connect handle into `bad`, changes the UUID to a random GUID, and asserts that `OpenDomain` returns `NT_STATUS_RPC_SS_CONTEXT_MISMATCH`. It then changes the copied handle type to `SAMR_HANDLE_USER` and expects the same mismatch.

After confirming a valid domain open, the test copies the domain handle and changes its type before `OpenUser` and `OpenGroup`. `OpenUser` with `SAMR_HANDLE_ALIAS` must fail with context mismatch; resetting the type to `SAMR_HANDLE_DOMAIN` must allow opening RID 501. `OpenGroup` with `SAMR_HANDLE_GROUP` as the domain handle type must fail; resetting to domain type must allow opening RID 513. Opened user/group/connect handles are closed.

## State and Persistence Behavior

The test does not create accounts or modify domain state. It uses fixed well-known RIDs and transient policy handles. The only state mutation is local tampering of copied `policy_handle` structures before sending requests.

## Dependencies and Integration Points

The file depends on generated SAMR NDR bindings, the torture RPC framework, loadparm workgroup configuration, GUID generation, and `NTSTATUS` assertion helpers. It integrates as a single test named `OpenDomainHandleType` under the `samr.handletype` suite.

## Risks and Edge Cases

The test assumes RID 501 and RID 513 exist and are openable in the target domain. It also assumes the client-visible `policy_handle` structure exposes and honors `uuid` and `handle_type` in a way that can be safely tampered for negative tests. One assertion after `OpenGroup` checks `ou.out.result` rather than `og.out.result`, which can mask an `OpenGroup` result failure after a successful transport call.

## Test Signals

The key signal is exact `NT_STATUS_RPC_SS_CONTEXT_MISMATCH` for random-GUID and wrong-handle-type requests, followed by successful operation with the same handle restored to the expected domain type. A failure indicates the server accepts mismatched SAMR contexts, returns a different context error, or no longer supports the assumed well-known objects.
