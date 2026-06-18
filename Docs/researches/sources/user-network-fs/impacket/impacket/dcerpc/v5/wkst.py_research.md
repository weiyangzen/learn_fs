# sources/user-network-fs/impacket/impacket/dcerpc/v5/wkst.py

## Purpose

`wkst.py` implements Impacket's client-side model for the Microsoft Workstation Service RPC interface, `[MS-WKST]`, exposed through interface UUID `6BFFD098-A112-3610-9833-46C3F87E345A` version `1.0`. The file is almost entirely declarative NDR/RPC schema plus thin helper functions: it defines workstation information levels, user/transport/use enumeration containers, domain join and computer-name RPC request/response records, and maps opnums to request/response classes for `dce.request()`.

## Important APIs, Types, And Functions

The exported RPC constants cover use status/type/force levels (`USE_OK`, `USE_DISKDEV`, `USE_LOTS_OF_FORCE`), join flags (`NETSETUP_JOIN_DOMAIN`, `NETSETUP_ACCT_CREATE`, `NETSETUP_MACHINE_PWD_PASSED`, and related flags), `MAX_PREFERRED_LENGTH`, and password buffer sizing for join password structures. `DCERPCSessionError` wraps `DCERPCException` and renders Windows error codes through `system_errors.ERROR_MESSAGES`.

The NDR model is built from `NDRSTRUCT`, `NDRUNION`, `NDRENUM`, `NDRPOINTER`, and conformant/fixed arrays. Core structures include `WKSTA_INFO_100/101/102/502/1013/1018/1046` and the selector union `WKSTA_INFO`; `WKSTA_USER_INFO_0/1`, array/container wrappers, and `WKSTA_USER_ENUM_STRUCT`; `WKSTA_TRANSPORT_INFO_0` and `WKSTA_TRANSPORT_ENUM_STRUCT`; `STAT_WORKSTATION_0`; domain join support structures such as `JOINPR_USER_PASSWORD`, `JOINPR_ENCRYPTED_USER_PASSWORD`, `UNICODE_STRING_ARRAY`, and `NET_COMPUTER_NAME_ARRAY`; and network-use structures `USE_INFO_0/1/2/3`, `USE_INFO`, and `USE_ENUM_STRUCT`.

RPC call classes run from `NetrWkstaGetInfo` through `NetrEnumerateComputerNames`. `OPNUMS` registers implemented operations: get/set workstation info, enumerate users/transports/uses, add/get/delete uses, get statistics, get join information, join/unjoin/rename/validate names, enumerate joinable OUs, add/remove/set computer names, and enumerate computer names. Convenience helpers prefixed with `h` allocate the request class, set nested union tags, normalize nullable strings with `checkNullString()`, insert `NULL` where supported, and call `dce.request(request)`.

## Control Flow

There is no autonomous runtime loop. Normal integration flow is: a caller binds a DCE/RPC transport to `MSRPC_UUID_WKST`, imports `OPNUMS` for request dispatch, then either instantiates a request manually or calls one of the helpers. Helper methods construct nested NDR records carefully: enumeration helpers set `Level` plus the union discriminant (`tag`) to the same value, set resume handles and preferred lengths, and then send. Mutating helpers for workstation info and uses set the outer level and populate the corresponding union arm (`WkstaInfo%d`, `UseInfo%d`). Domain join/name helpers normalize domain/account/computer strings to NUL-terminated values and conditionally pass password pointers as `NULL` or an encrypted password buffer.

## State And Persistence

The module keeps no local persistent state. All meaningful state is remote workstation-service state manipulated or queried through RPC. Locally, request objects only hold marshaling state until `dce.request()` serializes them. Resume handles are caller-provided or server-returned pagination cursors. Password buffers are in-memory NDR fields and are not encrypted by this file; it models the encrypted password container expected by the protocol.

## Dependencies And Integration Points

The file depends on Impacket's DCE/RPC NDR runtime (`impacket.dcerpc.v5.ndr`), common DCE/RPC data types (`dtypes`), enum support, UUID conversion, RPCRT exception base classes, and Windows system error descriptions. It integrates with the broader Impacket RPC stack through `OPNUMS`, `MSRPC_UUID_WKST`, and `dce.request()`. Consumers are typically SMB/RPC examples, tests under Impacket's SMB_RPC suite, and tools that inspect workstation domain membership, logged-on workstation users, mapped network uses, or computer names.

## Risks And Edge Cases

The helpers assume a conventional null server-name sentinel of ten NUL characters and may not expose all server-name forms a caller could set manually. Union tags must match info levels; mismatches marshal incorrect arms or fail remotely. `checkNullString()` indexes the last character and therefore assumes non-empty strings unless the caller passes `NULL`. Domain join calls carry sensitive credential material in memory and rely on the caller to supply correctly encrypted/obfuscated password buffers. Some opnums from the protocol are not implemented, such as transport delete. Tests should also watch the duplicate constant names for `NETSETUP_ACCT_DELETE` and `NETSETUP_ACCT_CREATE`; they are identical numeric values but later assignments shadow earlier symbols in Python.

## Test Signals

Useful tests instantiate each request class and verify NDR round-trip layout, union tag selection for levels 0/1/2/3/100/101/102/502, and helper-populated request fields. Integration tests need a bound workstation service to exercise `hNetrWkstaGetInfo`, enumeration pagination, and error rendering. Negative tests should include non-NUL strings, `NULL` passwords, unsupported levels, empty strings to `checkNullString()`, and server error codes to validate `DCERPCSessionError.__str__()`.
