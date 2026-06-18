# sources/user-network-fs/samba/source4/torture/rpc/dsgetinfo.c

## Purpose
`dsgetinfo.c` is a DRSUAPI `DsReplicaGetInfo` torture test based on `dssync.c`. It binds to DRSUAPI with sealed/signed RPC, discovers the LDAP default naming context, and exercises many replica info types, including linked-object metadata variants.

## Important APIs, types, and functions
`struct DsGetinfoBindInfo` stores pipe, binding handle, bind request, bind GUID, local/peer bind info, and policy handle. `struct DsGetinfoTest` stores the parsed DRSUAPI binding, LDAP/site/domain strings, and admin credentials/bind state. Key functions are `torture_get_ldap_base_dn`, `test_create_context`, `_test_DsBind`, `test_getinfo`, fixture setup/teardown, and `torture_drs_rpc_dsgetinfo_tcase`. It calls `dcerpc_parse_binding`, `dcerpc_binding_set_flags(DCERPC_SIGN | DCERPC_SEAL)`, `dcerpc_pipe_connect_b`, `dcerpc_drsuapi_DsBind_r`, `dcerpc_drsuapi_DsReplicaGetInfo_r`, `dcerpc_drsuapi_DsUnbind_r`, LDB connect/search helpers, and `dsdb_search_dn`.

## Control flow
Setup creates a context from the configured `binding` string, enables signing and sealing, prepares a max-extension `DsBindInfo28`, connects as admin credentials, and binds. `test_getinfo` obtains the domain DN by opening LDAP to the same RPC host and reading `defaultNamingContext`. It skips the replica-info loop when `torture:samba4` is true. Otherwise it iterates a table of DRSUAPI get-info levels and infotypes, builds level 1 or level 2 requests, appends the domain DN to object DN prefixes ending in a comma, applies optional flags, and accepts either success, enum-value-out-of-range transport status, or `WERR_INVALID_LEVEL` as a not-yet-supported signal. Teardown unbinds if the handle exists and frees the context.

## State and persistence behavior
The module does not create directory objects. It creates an RPC bind handle and an LDAP connection; teardown attempts `DsUnbind`. The test reads replication metadata for the domain naming context and for `CN=Domain Admins,CN=Users,<domain DN>` in selected rows. In-memory peer bind info is normalized from returned bind-info lengths 24, 28, 32, 48, or 52 into a `DsBindInfo28` view.

## Dependencies and integration points
It integrates DRSUAPI RPC, LDAP/LDB, DSDB helpers, GENSEC-related includes, Samba command-line credentials, module path resolution for LDB modules, and the DRS torture suite via `torture_drs_rpc_dsgetinfo_tcase()`. It requires a valid `binding` torture setting and credentials with enough directory replication/read metadata permissions.

## Risks and edge cases
LDAP discovery can fail independently of RPC bind, causing the whole test to fail before RPC coverage. The `no_invalid_levels` return value deliberately makes `WERR_INVALID_LEVEL` a soft discovery signal during the loop but a final false result, so partial server support is reported. Some table fields, such as `attribute_name`, are present but not populated in the current rows. Servers with different metadata availability or permission filtering may return implementation-specific errors.

## Test signals
Signals include successful signed/sealed bind, resolved default naming context, per-infotype NTSTATUS success or `NT_STATUS_RPC_ENUM_VALUE_OUT_OF_RANGE`, request-level `WERR_OK`, and `WERR_INVALID_LEVEL` comments for unsupported levels. The final boolean distinguishes full support from not-yet-supported levels.
