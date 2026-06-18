# sources/user-network-fs/impacket/impacket/dcerpc/v5/lsat.py

## Purpose

`lsat.py` implements the MS-LSAT lookup interface for translating account names to SIDs and SIDs to names through the LSA RPC endpoint. It shares the same interface UUID as LSAD but focuses on lookup-only structures, request/response classes, `OPNUMS`, and helper constructors.

## Important APIs, Types, and Functions

The main constant is `MSRPC_UUID_LSAT`. `POLICY_LOOKUP_NAMES` is the lookup-specific access mask. `DCERPCSessionError` formats NTSTATUS values. Data model types include `LSAPR_REFERENCED_DOMAIN_LIST`, translated SID/name variants (`LSA_TRANSLATED_SID`, `LSAPR_TRANSLATED_SID_EX`, `LSAPR_TRANSLATED_SID_EX2`, `LSAPR_TRANSLATED_NAME`, and `LSAPR_TRANSLATED_NAME_EX`), `LSAP_LOOKUP_LEVEL`, `LSAPR_SID_ENUM_BUFFER`, and `RPC_UNICODE_STRING_ARRAY`.

RPC calls map opnums 14, 15, 45, 57, 58, 68, 76, and 77 for `LsarLookupNames`, `LsarLookupSids`, `LsarGetUserName`, and v2/v3/v4 lookup variants. Helpers include `hLsarGetUserName`, `hLsarLookupNames`, `hLsarLookupNames2`, `hLsarLookupNames3`, `hLsarLookupNames4`, `hLsarLookupSids`, and `hLsarLookupSids2`.

## Control Flow

Callers typically use `lsad.hLsarOpenPolicy*` with `POLICY_LOOKUP_NAMES` or another suitable mask, then pass the policy handle to LSAT helpers. Name lookup helpers set `Count`, append `RPC_UNICODE_STRING` items, set the translated SID array to `NULL`, assign lookup level and revision fields, and call `dce.request`. SID lookup helpers convert canonical SID strings into `PRPC_SID` objects with `fromCanonical`, initialize translated names to `NULL`, and issue the request. `LsarLookupNames4` and `LsarLookupSids3` are handle-less variants intended for newer lookup flows.

## State and Persistence Behavior

The module is stateless and read-oriented. Remote state is only queried, not modified. Returned domain lists and translated arrays are transient NDR response objects. `MappedCount` is passed as a scalar field in request classes but helpers leave it at the NDR default and rely on the server to populate response counts.

## Dependencies and Integration Points

It depends on common dtypes, `samr.SID_NAME_USE`, `lsad.LSAPR_HANDLE`, `PLSAPR_TRUST_INFORMATION_ARRAY`, `ndr.py`, `rpcrt`, `nt_errors`, and UUID conversion. It integrates tightly with LSAD policy-handle acquisition and with Impacket callers that need account resolution before SAMR, LSAD, or Netlogon operations.

## Risks and Edge Cases

Only some newer operations have helpers; `LsarLookupSids3` and `LsarLookupNames4` classes exist but helper coverage is incomplete for all combinations. The helpers accept raw names and canonical SID strings with minimal validation, so invalid encoding, missing NUL behavior in underlying string types, or malformed SIDs fail during packing or remotely. Large lookup batches rely on conformant-array serialization and should be tested for count and referent correctness. The same UUID as LSAD means binding context and opnum choice are the meaningful distinction.

## Test Signals

Tests should validate helper-generated request fields, array lengths, SID conversion, and union-free response parsing. Integration signals include lookup of well-known SIDs and names, partial mappings that return nonzero `MappedCount`, unknown names, and v2/v3 behavior on domain controllers with different lookup levels.
