# sources/user-network-fs/samba/source4/torture/rpc/drsuapi_w2k8.c

## Purpose
`drsuapi_w2k8.c` tests DRSUAPI behavior as a Windows Server 2008-style client. Its focus is `DsBind` with a 48-byte bind info structure and `DsGetDomainControllerInfo` level 3, which requires newer extension negotiation.

## Important APIs, types, and functions
The file uses `struct DsPrivate_w2k8`, `test_DsBind_w2k8`, `test_DsGetDomainControllerInfo_w2k8`, `test_DsUnbind_w2k8`, common W2K8 setup/teardown helpers, and `torture_rpc_drsuapi_w2k8_tcase`. `test_DsBind_w2k8` fills `drsuapi_DsBindInfo48`, advertises the same core extension family as the normal DRS tests plus `DRSUAPI_SUPPORTED_EXTENSION_LH_BETA2` in `supported_extensions_ext`, and caches the returned bind info.

## Control flow
Fixture setup opens the DRSUAPI pipe, joins the domain as a temporary server trust account, and performs W2K8 bind. The registered tests include a direct bind test and a level-3 DC-info test. The DC-info test binds first, extracts `supported_extensions_ext` from returned bind-info lengths 32 or 48, asserts LH_BETA2 support, then queries level 3 against NetBIOS and DNS domain names plus unknown names expecting object-not-found. Successful results are searched for the joined DC's NetBIOS name and cached as `dcinfo`.

## State and persistence behavior
The test creates a temporary domain server-trust account in setup and removes it in teardown. It caches the bind GUID, bind handle, server bind info, and level-3 DC info in memory. It has no explicit unbind in registered teardown, though `test_DsUnbind_w2k8` exists and can be reused by callers.

## Dependencies and integration points
It depends on generated DRSUAPI client stubs, Samba torture RPC/domain-join helpers, loadparm, and `drsuapi.h` assertion macros. It complements the normal DRS tests by validating a newer wire contract and DC-info response shape (`drsuapi_DsGetDCInfo3`).

## Risks and edge cases
The level-3 test requires server support for LH_BETA2; older or partial implementations fail early. The loop over domain names contains a `break` before the final `torture_assert(found, ...)`, making that assertion unreachable and limiting checks to the first successful iteration. Setup performs a bind, and the DC-info test performs another bind without an intervening unbind, which is acceptable for the harness but relevant for handle tracking.

## Test signals
Pass signals are NTSTATUS success, `WERR_OK` from bind and level-3 DC-info calls for known names, `WERR_DS_OBJ_NOT_FOUND` for unknown names, non-null bind info, and negotiated LH_BETA2 support. The cached level-3 DC record is the main data signal.
