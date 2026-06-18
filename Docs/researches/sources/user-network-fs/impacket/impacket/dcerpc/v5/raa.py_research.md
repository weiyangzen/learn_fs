# sources/user-network-fs/impacket/impacket/dcerpc/v5/raa.py

## Purpose

`raa.py` implements the client-side Remote Authorization API Protocol [MS-RAA]. It lets callers create authorization contexts from SIDs, combine user and device contexts, run remote access checks against one or more security descriptors, query context information, modify claims, modify SIDs, and free context handles.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_RAA`, default object UUID constants, `AUTHZ_COMPUTE_PRIVILEGES`, security attribute flags and value type constants, and three NDR enum classes: `AUTHZ_CONTEXT_INFORMATION_CLASS`, `AUTHZ_SECURITY_ATTRIBUTE_OPERATION`, and `AUTHZ_SID_OPERATION`.

Core structures include `AUTHZR_HANDLE`, `SR_SD`, `AUTHZR_ACCESS_REQUEST`, `AUTHZR_ACCESS_REPLY`, `AUTHZR_SID_AND_ATTRIBUTES`, `AUTHZR_TOKEN_USER`, custom `AUTHZR_TOKEN_GROUPS`, security attribute string/union/value arrays, `AUTHZR_SECURITY_ATTRIBUTES_INFORMATION`, and `AUTHZR_CONTEXT_INFORMATION`. RPC calls cover opnums 0 through 6: `AuthzrFreeContext`, `AuthzrInitializeContextFromSid`, `AuthzrInitializeCompoundContext`, `AuthzrAccessCheck`, `AuthzGetInformationFromContext`, `AuthzrModifyClaims`, and `AuthzrModifySids`.

Helpers mirror those calls: `hAuthzrFreeContext`, `hAuthzrInitializeContextFromSid`, `hAuthzrInitializeCompoundContext`, `hAuthzrAccessCheck`, `hAuthzGetInformationFromContext`, `hAuthzrModifyClaims`, and `hAuthzrModifySids`. `_enum_operation` coerces raw integer operations into the expected NDR enum wrapper.

## Control Flow

Initialization from SID converts a canonical SID string into `RPC_SID`, clears expiration time with `NULL`, zeros the `LUID`, and requests a context handle using the selected object UUID. Access checks construct an `AUTHZR_ACCESS_REQUEST`, optionally attach an object type list, normalize a single security descriptor into a list, wrap each descriptor as `SR_SD`, initialize reply arrays with the requested result length, and call `dce.request(..., uuid=objectUuid)`.

The modify helpers set operation counts from the caller's operation list, append coerced enum values, and attach optional claims or SID/group arrays. `AUTHZR_TOKEN_GROUPS` has custom parser and serializer flow because observed NDR32 replies omit the conformant-array max count while NDR64 replies include it. Its methods manually handle alignment, group counts, entry serialization, and referent parsing.

## State And Persistence Behavior

There is no local persistence. Server-side authorization contexts are represented by `AUTHZR_HANDLE` values and must be freed by the caller. `hAuthzrModifyClaims` and `hAuthzrModifySids` mutate remote authorization context state for the lifetime of that context. `AuthzrAccessCheck` is read/evaluation-oriented but can reveal effective access and policy behavior for supplied descriptors.

The object UUID argument changes server behavior. `RAA_OBJECT_UUID_NO_SCOPED_POLICY_BIN` disables server-side stripping of `SYSTEM_SCOPED_POLICY_ID_ACE` entries during access checks, so callers must choose the object UUID intentionally.

## Dependencies And Integration Points

Dependencies include `struct.pack`, `struct.unpack_from`, Impacket NDR classes, dtypes such as `RPC_SID`, `OBJECT_TYPE_LIST`, `LUID`, and `ACCESS_MASK`, the local compatibility `Enum`, `system_errors`, `rpcrt.DCERPCException`, and UUID helpers. The module integrates with security descriptor builders/parsers elsewhere in Impacket and with `rpcrt` object UUID request support.

## Risks And Edge Cases

The security impact is medium to high because the module can model hypothetical group, SID, and claim changes and ask a remote host for resulting access. Callers can misuse it for reconnaissance of authorization boundaries. Context handles are server resources; failing to call `hAuthzrFreeContext` can leak server-side state until timeout.

Parsing risk is concentrated in `AUTHZR_TOKEN_GROUPS`, whose custom NDR32/NDR64 behavior is based on observed Windows replies. Malformed or alternate server encodings can desynchronize offsets. The boolean security attribute maps to a `ULONGLONG` field named `Uint64`, which may surprise callers. `DCERPCSessionError` is defined at the end of the file after helpers, which works at runtime but is easy to miss during review.

## Test Signals

Tests should cover canonical SID conversion, context initialization request layout, compound context handle assignment, access checks with one and multiple security descriptors, object type lists, result lengths greater than one, and both object UUID modes. Parser tests should round-trip `AUTHZR_TOKEN_GROUPS` in NDR32 and NDR64 with zero, one, and multiple groups. Modify tests should verify enum coercion from both raw integers and enum instances. Integration tests should run against a Windows host and compare granted masks with local AuthZ expectations for known descriptors.
