# sources/user-network-fs/impacket/impacket/dcerpc/v5/nspi.py

## Purpose

`nspi.py` implements Impacket's client-side NDR model for the Name Service Provider Interface protocols [MS-NSPI] and [MS-OXNSPI], primarily for Exchange address book access. It defines NSPI constants, MAPI property wire types, entry ID packet structures, request/response classes, opnum mappings, and helper functions for binding to an NSPI server, browsing rows, resolving names, converting distinguished names to minimal entry IDs, querying property columns, and simplifying returned MAPI property rows into Python values.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_NSPI`, `DCERPCSessionError`, many NSPI constants, and the `handle_t` context handle. Its property model is centered on `PropertyTagArray_r`, `Binary_r`, scalar and multivalue array structures, `PROP_VAL_UNION`, `PropertyValue_r`, `PropertyRow_r`, and `PropertyRowSet_r`. Restriction support is partly modeled through `Restriction_r`, `AndRestriction_r`, `ContentRestriction_r`, `PropertyRestriction_r`, and `RestrictionUnion_r`, but matching-related RPC calls are commented out.

Entry identifiers are represented by packet `Structure` classes `EphemeralEntryID` and `PermanentEntryID`, with `GUID_NSPI` used to identify permanent NSPI entry IDs. `STAT` carries cursor and sorting state for table operations. RPC call classes cover opnums 0, 1, 2, 3, 4, 7, 8, 9, 10, 12, 13, 14, 16, 17, 18, 19, and 20. Implemented helpers include `hNspiBind`, `hNspiUnbind`, `hNspiUpdateStat`, `hNspiQueryRows`, `hNspiSeekEntries`, `hNspiDNToMId`, `hNspiGetPropList`, `hNspiGetProps`, `hNspiGetSpecialTable`, `hNspiGetTemplateInfo`, `hNspiModLinkAtt`, `hNspiQueryColumns`, `hNspiGetNamesFromIDs`, `hNspiResolveNames`, and `hNspiResolveNamesW`.

Conversion helpers include `get_guid_from_dn`, `get_dn_from_guid`, `getUnixTime`, `simplifyPropertyRow`, and `simplifyPropertyRowSet`. `EXCH_SID` wraps `LDAP_SID` string formatting, and `ExchBinaryObject` marks opaque Exchange binary values.

## Control Flow

Most protocol behavior is declarative NDR layout. Request helpers allocate an `NDRCALL`, populate a context handle, flags, `STAT` state, arrays, and property tag counts, then call `dce.request()`. Bind sets a default Teletex code page when the caller does not provide a `STAT`. Unbind and update-stat call `dce.request(..., checkError=False)` because NSPI may return useful state alongside non-zero status codes.

Table helpers build optional property tag and entry-table arrays manually. `hNspiQueryRows`, `hNspiSeekEntries`, `hNspiGetProps`, `hNspiGetNamesFromIDs`, and the resolve-name helpers append `DWORD` or string wrapper instances and then adjust `cValues`, `Count`, and sometimes nested `MaximumCount` fields to satisfy conformant varying array encoding. `hNspiSeekEntries` forces `SortTypeDisplayName` and a Unicode display-name target because MS-OXNSPI rejects other combinations in that code path. `hNspiModLinkAtt` converts caller-supplied entry IDs into `Binary_r` values by calling `getData()`.

`simplifyPropertyRow` is the main response post-processor. It inspects the active union arm, converts integer NDR wrappers to Python ints, removes null terminators from strings, turns selected binary property tags into SIDs, GUID strings, permanent or ephemeral entry ID structures, UTF-8 strings, or signed integers, maps file times into `datetime.fromtimestamp()`, and leaves unknown values as raw wrapper objects or `ExchBinaryObject`.

## State And Persistence Behavior

There is no disk persistence. Runtime state lives in server-side NSPI context handles returned by `NspiBind`, client-maintained `STAT` cursor fields, request arrays, and returned row sets. The caller is responsible for retaining the context handle and passing it to later operations, then releasing it with `hNspiUnbind`. Some helpers use mutable default arguments such as `pPropTags=[]`, `lpETable=[]`, and `paStr=[]`; they do not mutate those defaults directly in normal paths, but this pattern is still risky for future changes.

Remote effects are mostly read-oriented except `hNspiModLinkAtt`, which can modify a link attribute on an address book object when the caller has permission. Name resolution and row queries disclose Exchange address book data.

## Dependencies And Integration Points

The module depends on Impacket NDR primitives, common Windows types from `dtypes.py`, `Structure`, UUID helpers, `mapi_constants`, HRESULT errors, `LDAP_SID`, `six.PY2`, and Python `datetime`, `struct`, and `binascii`. It integrates with `rpcrt.DCERPC.request()` and is typically used over normal DCE/RPC transports or through `rpch.py` RPC-over-HTTP connections to Exchange ports. `oxabref.py` complements this module by finding an address book referral target.

## Risks And Edge Cases

The module has broad protocol coverage but explicitly leaves some calls commented out, including `NspiGetMatches`, `NspiResortRestriction`, `NspiModProps`, and an undocumented delete call. The restriction model is therefore structurally present but not fully exercised by helpers. Manual nested count manipulation is fragile; wrong `MaximumCount` or `cValues` values can produce malformed NDR. `hNspiSeekEntries` accepts a `SortType` argument but ignores it and always uses `SortTypeDisplayName`.

`simplifyPropertyRow` relies on property-tag-specific heuristics and can misclassify unknown binary values. Its file-time conversion uses local timezone semantics via `datetime.fromtimestamp()`. `checkNullString` indexes `string[-1:]`, so empty strings work by Python slicing behavior but non-string byte/text mismatches can still matter. `get_guid_from_dn` trusts the last `=` component of a DN and does not validate the result before UUID conversion.

## Test Signals

Unit tests should serialize each helper with a fake DCE object and verify opnum, handle assignment, array counts, null termination, and `checkError` behavior. Property simplification tests should cover scalar, string, binary, SID, GUID, permanent entry ID, ephemeral entry ID, multivalue, and file-time cases. Parser tests need captured Exchange row sets with null pointers and uncommon property tags. Integration tests require an Exchange or NSPI-compatible endpoint and should verify bind, query columns, special table, resolve names, DN-to-MID, get props, and unbind workflows.
