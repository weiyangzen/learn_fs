# sources/user-network-fs/samba/source4/torture/rpc/drsuapi.c

## Purpose
`drsuapi.c` is the main Samba torture test case for Active Directory DRSUAPI replication RPCs. It verifies bind negotiation, domain controller discovery, SPN writes, replica metadata queries, replica sync/update reference calls, `DsGetNCChanges`, site cost lookup, unbind, and association-group behavior across multiple DCE/RPC pipes and credential types.

## Important APIs, types, and functions
The file uses `struct DsPrivate` from `drsuapi.h` as shared fixture state: admin and DC credentials, DRS pipe, bind handle, server bind info, domain identifiers, DC info, and temporary domain join handle. Core helpers include `test_DsBind`, `test_DsGetDomainControllerInfo`, `test_DsWriteAccountSpn`, `test_DsReplicaGetInfo`, `test_DsReplicaSync`, `test_DsReplicaUpdateRefs`, `test_DsGetNCChanges`, `test_QuerySitesByCost`, `test_DsUnbind`, `torture_rpc_drsuapi_get_dcinfo`, and the common setup/teardown functions. It calls generated stubs such as `dcerpc_drsuapi_DsBind_r`, `DsGetDomainControllerInfo_r`, `DsWriteAccountSpn_r`, `DsReplicaGetInfo_r`, `DsReplicaSync_r`, `DsReplicaUpdateRefs_r`, `DsGetNCChanges_r`, `QuerySitesByCost_r`, and `DsCrackNames_r`.

## Control flow
`torture_rpc_drsuapi_tcase()` registers one fixture-backed tcase. Setup opens the DRSUAPI pipe, joins the domain as a temporary BDC-like server trust account named from `torturetest` plus a random suffix, binds using a `DsBindInfo28` request advertising many extensions, and gathers DC info. Tests then run independent DRS operations using the cached bind handle. Association-group tests open two pipes in the same association group, bind on one, run `DsCrackNames` on both, close the first, and verify the second still works. The workstation association test temporarily joins a workstation account and leaves it after the check.

## State and persistence behavior
The suite creates a temporary domain machine account during setup and removes it in teardown with `torture_leave_domain`. `test_DsWriteAccountSpn` adds two `smbtortureSPN/*` SPNs to the joined DC computer object and deletes them immediately. `test_DsReplicaUpdateRefs` creates a random destination DSA DNS name, exercises delete/add/duplicate/reset/delete/replace/delete flows, and expects cleanup through final delete. `DsReplicaSync` is gated behind the `dangerous` torture setting because it can trigger replication behavior. `DsGetNCChanges` and metadata queries are read-oriented but can be heavy.

## Dependencies and integration points
This module depends on DRSUAPI generated bindings, domain join helpers, Samba command-line credentials, GUID/SID utilities, loadparm settings, and the companion `drsuapi_cracknames.c` test function. It is tightly integrated with AD semantics and assumes a writable domain controller unless `samba4` skip gates apply.

## Risks and edge cases
Failures between mutation and cleanup can leave SPNs, replica refs, or temporary computer accounts. Several tests skip or alter expectations for Samba4 or dangerous mode, so coverage changes by environment. Random names reduce collision risk but do not make cleanup transactional. `test_DsGetDomainControllerInfo` has a `found` flag that is not reset inside every domain-name iteration, which can hide per-iteration misses after a previous success. Some calls intentionally use random GUIDs and zero high-watermarks, which may be expensive or rejected by stricter servers.

## Test signals
Pass signals combine NTSTATUS success and `WERR_OK` through `torture_drsuapi_assert_call`. Negative expectations include unknown domains returning `WERR_DS_OBJ_NOT_FOUND`, deleting a missing replica ref returning `WERR_DS_DRA_REF_NOT_FOUND`, duplicate add returning `WERR_DS_DRA_REF_ALREADY_EXISTS`, and unsupported replica info returning `NT_STATUS_RPC_ENUM_VALUE_OUT_OF_RANGE`. Dangerous and Samba4 skip comments are explicit runtime signals.
