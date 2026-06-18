# sources/user-network-fs/impacket/impacket/dcerpc/v5/oxabref.py

## Purpose

`oxabref.py` implements the Address Book Name Service Provider Interface Referral Protocol [MS-OXABREF]. It is a small Exchange address book referral binding that asks an RPC endpoint for a suitable NSPI server or converts a mailbox server distinguished name into a server FQDN.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_OXABREF`, `DCERPCSessionError`, pointer wrappers `PUCHAR_ARRAY` and `PPUCHAR_ARRAY`, and two RPC calls: `RfrGetNewDSA` at opnum 0 and `RfrGetFQDNFromServerDN` at opnum 1. `OPNUMS` maps both calls to their response classes.

Helper functions are `hRfrGetNewDSA(dce, pUserDN='')` and `hRfrGetFQDNFromServerDN(dce, szMailboxServerDN)`. `checkNullString` is the shared local helper that preserves `NULL` and appends a C-style null terminator to non-null strings.

## Control Flow

`hRfrGetNewDSA` builds an opnum 0 request with flags set to zero, a null-terminated user DN, `ppszUnused` set to `NULL`, and an initialized `ppszServer` output pointer. It sends the request and strips the trailing null from `ppszServer`; it attempts the same for `ppszUnused` when the original request field was not `NULL`.

`hRfrGetFQDNFromServerDN` null-terminates the mailbox server DN, sets `cbMailboxServerDN` to the resulting string length, sends opnum 1, and strips the returned FQDN terminator. Error rendering first checks MAPI constants and then generic HRESULT messages.

## State And Persistence Behavior

There is no local persistence and no durable module state. Calls are stateless client requests over a bound DCE connection. Remote state is read-only from this client's perspective: the server chooses or reports address book referral information.

## Dependencies And Integration Points

The module depends on `hresult_errors`, `mapi_constants`, `STR`, `ULONG`, `NULL`, NDR call/pointer classes, `rpcrt.DCERPCException`, and UUID helpers. It integrates with Exchange address book workflows by supplying server names used by `nspi.py` over regular DCE/RPC or RPC-over-HTTP.

## Risks And Edge Cases

String and pointer handling are the main risks. `PUCHAR_ARRAY` uses `STR`, so callers need to provide byte/string values compatible with Impacket's `STR` encoding rules. `hRfrGetNewDSA` tests `request['ppszUnused']` rather than the response before trimming `resp['ppszUnused']`, so it will not trim a non-null server-filled unused pointer when the request passed `NULL`. `checkNullString` assumes sliceable string-like input. Response trimming assumes returned strings are non-empty and null-terminated.

## Test Signals

Tests should verify that both helpers set flags, byte counts, and null terminators correctly, and that response strings are trimmed. A fake DCE object can assert opnum selection and request field layout. Error tests should cover MAPI errors, HRESULT errors, and unknown status values. Integration tests should pair `hRfrGetNewDSA` with `nspi.hNspiBind` against an Exchange endpoint.
