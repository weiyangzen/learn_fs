# sources/user-network-fs/impacket/impacket/dcerpc/v5/lsad.py

## Purpose

`lsad.py` implements the MS-LSAD Local Security Authority Policy interface for Impacket's DCE/RPC v5 stack. It is mostly an IDL-to-Python mapping: access-mask constants, policy/account/secret/trust structures, discriminated unions keyed by LSAD enum values, RPC request/response classes, an `OPNUMS` dispatch table, and helper functions that populate common request fields before calling `dce.request`.

## Important APIs, Types, and Functions

The module exports `MSRPC_UUID_LSAD`, `DCERPCSessionError`, policy/account/secret/trusted-domain access constants, and many NDR types. Core handle and string types are `LSAPR_HANDLE`, `LSA_UNICODE_STRING`, and local `STRING`. Policy object modelling centers on `LSAPR_OBJECT_ATTRIBUTES`, `SECURITY_QUALITY_OF_SERVICE`, `LSAPR_POLICY_INFORMATION`, `LSAPR_POLICY_DOMAIN_INFORMATION`, and pointer wrappers such as `PLSAPR_POLICY_INFORMATION`. Account and rights structures include `LSAPR_ACCOUNT_ENUM_BUFFER`, `LSAPR_USER_RIGHT_SET`, `LSAPR_PRIVILEGE_SET`, and `LSAPR_PRIVILEGE_ENUM_BUFFER`. Secret/private-data support uses `LSAPR_CR_CIPHER_VALUE` and pointer-to-pointer wrappers for query responses. Trust and forest-trust modelling includes `LSAPR_TRUSTED_DOMAIN_INFO`, `LSAPR_TRUSTED_ENUM_BUFFER(_EX)`, `LSA_FOREST_TRUST_RECORD`, `LSA_FOREST_TRUST_INFORMATION`, and collision record types.

RPC call classes cover policy open/query/set, account create/open/enumerate/rights/privileges/system-access, secret create/open/set/query, private data store/retrieve, trusted-domain enumeration, privilege lookup/enumeration, security descriptor query/set, delete, and close. Helpers include `hLsarOpenPolicy2`, `hLsarQueryInformationPolicy*`, `hLsarEnumerateAccounts*`, `hLsarAddAccountRights`, `hLsarStorePrivateData`, `hLsarQuerySecurityObject`, and related request builders.

## Control Flow

Callers bind to the LSAD UUID, open a policy handle, then pass returned handles into subsequent helpers. Helpers construct an `NDRCALL` subclass, assign handles, SIDs, strings, arrays, and access masks, then delegate serialization and transport to the DCE/RPC object. Responses carry NTSTATUS `ErrorCode` fields plus handles, union pointers, enumeration buffers, or byte arrays. Unions are selected by assigning enum-backed information classes before serialization or by response tags during deserialization.

## State and Persistence Behavior

The module stores no durable local state. It operates on remote LSA state: policy configuration, account rights, privileges, secrets/private data, trusted-domain records, and security descriptors. Local handles are opaque 20-byte NDR structs. Enumeration helpers expose context arguments for trusted-domain and privilege enumeration, but `hLsarEnumerateAccounts` always starts with the request default context.

## Dependencies and Integration Points

`lsad.py` depends on `ndr.py` for serialization, `dtypes.py` for common RPC types, `enum.py` for enum values, `rpcrt.DCERPCException`, `nt_errors`, and UUID conversion. Other modules import its types, notably `lsat.py` for `LSAPR_HANDLE` and trust arrays, and `nrpc.py` for `STRING` and forest-trust pointers. It integrates with Impacket DCE/RPC transports and SMB/RPC tests.

## Risks and Edge Cases

Several protocol operations are declared only as comments and are not present in `OPNUMS`, so callers cannot rely on full LSAD coverage. `hLsarQueryDomainInformationPolicy` builds `LsarQueryInformationPolicy` rather than `LsarQueryDomainInformationPolicy`, which sends opnum 7 instead of opnum 53. `hLsarSetSecret` appears to instantiate `LsarOpenSecret` rather than `LsarSetSecret`, so its field assignments do not match the request class. Helpers expect callers to provide correctly encoded encrypted secret values and valid privilege/right structures; little validation is performed before network submission. Rights and secret operations are security-sensitive and require appropriate remote privileges.

## Test Signals

Useful tests include NDR round-trip coverage for policy/trusted-domain unions, helper field-population tests with a fake DCE object, and integration tests against a controlled Windows target for open/query/close, account-right enumeration, private-data store/retrieve, and security descriptor query. Regression tests should specifically assert the intended opnums for domain-policy query and secret-set helpers.
