# sources/user-network-fs/impacket/impacket/dcerpc/v5/drsuapi.py

## Purpose

`drsuapi.py` implements Impacket's client-side NDR model and helper routines for the [MS-DRSR] Directory Replication Service Remote Protocol. It defines constants, NDR structures, unions, RPC request/response classes, opnum mappings, and convenience helpers for binding to DRS, querying domain controller metadata, cracking directory names, requesting replication changes, and decrypting replicated secret attribute payloads.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_DRSUAPI` and `DCERPCSessionError`, plus protocol constants for extended operations, DRS extensions, replication flags, LDAP connection properties, name cracking formats, verification modes, and NT4 changelog modes. Core NDR types include `DRS_EXTENSIONS`, `DRS_EXTENSIONS_INT`, `DRS_HANDLE`, `DRS_MSG_DCINFOREQ/REPLY`, `DS_DOMAIN_CONTROLLER_INFO_*W`, `DRS_MSG_CRACKREQ/REPLY`, `DS_NAME_FORMAT`, `UPTODATE_VECTOR_*`, `USN_VECTOR`, `DSNAME`, `PARTIAL_ATTR_VECTOR_V1_EXT`, `SCHEMA_PREFIX_TABLE`, `ATTR*`, `ENTINF`, `REPLENTINFLIST`, `REPLVALINF_*`, and `DRS_MSG_GETCHGREQ/REPLY` variants.

RPC calls are represented by `DRSBind`, `DRSUnbind`, `DRSGetNCChanges`, `DRSVerifyNames`, `DRSGetNT4ChangeLog`, `DRSCrackNames`, and `DRSDomainControllerInfo`. `OPNUMS` maps opnums 0, 1, 3, 12, and 16; the verify and NT4 changelog classes exist but are not included in that table. Helpers include `hDRSUnbind`, `hDRSDomainControllerInfo`, `hDRSCrackNames`, `deriveKey`, `removeDESLayer`, `DecryptAttributeValue`, `MakeAttid`, and `OidFromAttid`.

## Control Flow

Most logic is declarative NDR layout. Request helpers create an NDRCALL, set version fields and union tags, populate strings or arrays, then call `dce.request()`. `hDRSDomainControllerInfo` forces input version 1 and union tag 1; `hDRSCrackNames` sets code page and locale to zero, fills offered/desired formats, and appends `LPWSTR` names. `DRS_MSG_GETCHGREQ` and `DRS_MSG_GETCHGREPLY` select versioned union arms by tag. `REPLENTINFLIST.fromString` rewrites `pNextEntInf` to a typed pointer before parsing to handle linked-list replies.

Crypto flow is procedural: `deriveKey` builds DES keys from a RID, `removeDESLayer` decrypts two DES blocks, and `DecryptAttributeValue` derives an RC4 key from MD5(session key + salt), decrypts an `ENCRYPTED_PAYLOAD`, and strips the checksum prefix. `MakeAttid` and `OidFromAttid` convert between LDAP OIDs and DRS `ATTRTYP` values using BER encoding and schema prefix tables.

## State And Persistence Behavior

There is no disk persistence. State is carried in NDR instances, DCE context handles, remote DRS handles, and caller-supplied prefix tables. `MakeAttid` mutates the caller's prefix table by adding missing OID prefixes. Remote effects can be significant: `DRSGetNCChanges` reads replicated directory content and may expose secret attributes when used with sufficient privileges.

## Dependencies And Integration Points

The file depends on Impacket NDR primitives, `dtypes.py`, `Structure`, UUID helpers, HRESULT/system error tables, `rpcrt.DCERPCException`, Kerberos crypto objects, `pyasn1`, `transformKey`, and optional `Cryptodome` ARC4/DES. It integrates with any connected and bound `DCERPC_v5` object and is used by AD replication and DCSync-style tooling.

## Risks And Edge Cases

The security blast radius is high because the module supports privileged directory replication and secret decryption. Crypto import failure is logged but not otherwise guarded. `DecryptAttributeValue` leaves checksum validation commented out. Parsing risk exists in recursive lists and unresolved `rgValues` modeling, which is represented as `DWORD` in V6/V9 replies. `VALUE_META_DATA_EXT_V3` repeats the field name `unused1`, and malformed prefix tables can break OID conversion.

## Test Signals

Tests should verify helper request construction, union tags, null termination, and name array counts. Round-trip tests for `MakeAttid`/`OidFromAttid` should cover small and large OID components. Crypto tests need known vectors for RID DES removal and DRS encrypted attributes. Parser tests should include captured DRS replies for V1, compressed V2/V7, V6/V9 object lists, malformed prefix tables, and absent optional pointers.
