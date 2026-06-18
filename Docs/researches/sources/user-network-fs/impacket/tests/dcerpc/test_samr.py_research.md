# sources/user-network-fs/impacket/tests/dcerpc/test_samr.py

## Purpose
This file is a remote integration test suite for Impacket's SAMR DCE/RPC implementation. It exercises both raw NDR request classes such as `SamrConnect`, `SamrOpenDomain`, `SamrQueryInformationUser2`, and convenience helpers such as `hSamrConnect`, `hSamrOpenUser`, and `hSamrSetInformationUser2`. Coverage spans server connection negotiation, domain lookup/open, user/group/alias enumeration, display information, object creation/deletion, membership management, security descriptors, password policy, and password-change calls.

## Important APIs, Types, and Functions
`SAMRTests` inherits `DCERPCTests`, binds `samr.MSRPC_UUID_SAMR`, requires authentication, and uses NTLM packet privacy. `get_domain_handle()` is the central helper: it connects to the SAM server, enumerates domains, looks up the first domain SID, and opens the domain with broad domain/server access masks. Tests directly instantiate many `impacket.dcerpc.v5.samr` request/structure types, including `RPC_SID`, `SAMPR_GROUP_INFO_BUFFER`, `SAMPR_ALIAS_INFO_BUFFER`, `SAMPR_PSID_ARRAY`, and `SAM_VALIDATE_INPUT_ARG`. Password-change tests also depend on `impacket.crypto` and `impacket.ntlm`.

## Control Flow
Most tests call `self.connect()`, derive a SAM server or domain handle, populate a request object, call `dce.request()`, and dump or assert the response. Paired raw/helper tests validate the same RPC path through low-level request classes and high-level `hSamr*` wrappers. Enumeration tests loop while `STATUS_MORE_ENTRIES` is returned and advance the `EnumerationContext`. Mutating tests usually query old values, set a temporary value, verify it with another query, then restore the previous value. Transport subclasses run the same test body over SMB named pipe and TCP, with NDR and NDR64 variants.

## State and Persistence Behavior
The suite mutates real SAM state on the configured remote target. It creates and deletes temporary users/aliases, changes domain password/logoff/OEM/replication fields, edits group/alias/user comments and names, adjusts group attributes, and performs password change flows. Several operations attempt to restore old values, but not all creation paths use `finally`, so failures may leave accounts, aliases, or modified metadata behind. The Unicode password path creates a random complex password containing non-ASCII characters before expecting a password policy failure.

## Dependencies and Integration Points
The file integrates with the shared DCE/RPC test harness in `tests.dcerpc`, the SAMR RPC definitions in `impacket.dcerpc.v5.samr`, shared DCE/RPC types in `dtypes`, NT status constants in `nt_errors`, NTLM hash helpers, and optional `Cryptodome.Cipher.ARC4`. It assumes a Windows SAM-compatible remote endpoint, Administrator and Guest RIDs, configured credentials on `DCERPCTests`, and sufficient privileges for many mutating operations.

## Risks
These are privileged destructive integration tests, not hermetic unit tests. Risks include persistent account or alias residue on failure, accidental modification of Administrator/user/domain fields, fragile assumptions about built-in RIDs and server names (`BETO`, `Administrator`, `Guest`), environment-specific status codes, and broad access masks that may fail under tighter policies. Some exception checks inspect stringified errors rather than numeric codes, which can be brittle across versions and locales.

## Test Signals
Signals include successful RPC marshalling/unmarshalling, expected `DCERPCSessionError` values such as `STATUS_NO_SUCH_ALIAS`, `STATUS_ACCESS_DENIED`, `STATUS_OBJECT_TYPE_MISMATCH`, `STATUS_INVALID_INFO_CLASS`, `STATUS_PASSWORD_RESTRICTION`, and `rpc_s_access_denied`, equality checks after set/query cycles, and round-trip SID/hash/password buffer behavior. The `pytest.mark.remote` classes signal that these tests require external infrastructure.
