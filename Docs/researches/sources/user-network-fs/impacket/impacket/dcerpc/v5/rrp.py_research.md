# sources/user-network-fs/impacket/impacket/dcerpc/v5/rrp.py

## Purpose

`sources/user-network-fs/impacket/impacket/dcerpc/v5/rrp.py` implements Impacket's Python bindings for the Windows Remote Registry Protocol, `[MS-RRP]`, over DCE/RPC. The file defines the RRP interface UUID, protocol constants, NDR structures, request/response classes keyed by opnum, and convenience helpers for opening registry roots, creating/opening/deleting keys, enumerating keys and values, querying and setting values, changing security descriptors, and saving/loading/restoring registry hives. The source was read as a complete 1020-line file for this report.

## Important APIs, Types, and Functions

The central wire type is `RPC_HKEY`, a context handle with `context_handle_attributes`, a UUID payload, and an `isNull()` helper that treats an all-zero UUID as a null handle. Value and security support types include `RVALENT`, `RVALENT_ARRAY`, `BYTE_ARRAY`, `PBYTE_ARRAY`, `RPC_SECURITY_DESCRIPTOR`, `RPC_SECURITY_ATTRIBUTES`, and `PRPC_SECURITY_ATTRIBUTES`. Constants cover registry access masks, registry value types such as `REG_SZ`, `REG_DWORD`, `REG_MULTI_SZ`, and `REG_QWORD`, and key restore/create flags.

The RPC call classes model opnums 0 through 35 where implemented: root open calls (`OpenClassesRoot`, `OpenCurrentUser`, `OpenLocalMachine`, `OpenPerformanceData`, `OpenUsers`, `OpenCurrentConfig`, `OpenPerformanceText`, `OpenPerformanceNlsText`), core key/value operations (`BaseRegCloseKey`, `BaseRegCreateKey`, `BaseRegOpenKey`, `BaseRegDeleteKey`, `BaseRegDeleteKeyEx`, `BaseRegDeleteValue`, `BaseRegEnumKey`, `BaseRegEnumValue`, `BaseRegQueryInfoKey`, `BaseRegQueryValue`, `BaseRegSetValue`), hive operations (`BaseRegLoadKey`, `BaseRegUnLoadKey`, `BaseRegReplaceKey`, `BaseRegRestoreKey`, `BaseRegSaveKey`, `BaseRegSaveKeyEx`, `BaseRegFlushKey`), security operations (`BaseRegGetKeySecurity`, `BaseRegSetKeySecurity`), versioning (`BaseRegGetVersion`), and multi-value query classes. `OPNUMS` binds each implemented opnum to the matching request and response type for DCE/RPC dispatch.

Helper functions are the user-facing API. `checkNullString()` adds a trailing UTF-16 logical terminator unless the caller passed `NULL`. `packValue()` and `unpackValue()` convert Python values to and from registry wire byte arrays for DWORD, QWORD, string, expand-string, and multi-string values. `hOpen*` helpers open predefined roots with `ServerName` set to `NULL`. `hBaseReg*` helpers fill request structures and call `dce.request()`, returning the raw response except where a helper deliberately normalizes the result, such as `hBaseRegQueryValue()` returning `(type, unpacked_value)` and `hBaseRegQueryMultipleValues()` returning a list of dictionaries.

## Control Flow

This module is declarative until a helper is called. The normal flow is: bind a DCE/RPC connection to `MSRPC_UUID_RRP`, call an `hOpen*` helper to obtain an `RPC_HKEY`, perform key or value requests with that handle, then close it with `hBaseRegCloseKey()`. Request classes define only field order and opnum; all network I/O is delegated to the supplied DCE/RPC object.

Several helpers contain important local control flow. `hBaseRegEnumValue()` and `hBaseRegQueryValue()` make an initial request with a caller-supplied buffer length, catch `DCERPCSessionError`, detect `system_errors.ERROR_MORE_DATA`, resize from the returned `lpcbData`, and retry. `hBaseRegEnumValue()` caps this at a single retry and logs before re-raising on repeated failure; `hBaseRegQueryValue()` keeps retrying while the server reports more data. `hBaseRegQueryInfoKey()` and `hBaseRegEnumKey()` manually set nested `MaximumLength` and `MaximumCount` fields because some servers rely on those input buffer lengths. `hBaseRegQueryMultipleValues()` builds an `RVALENT_ARRAY`, allocates a fixed 128-byte result buffer, sends the request, and reconstructs values by slicing `lpvalueBuf` with returned offsets and lengths.

## State and Persistence Behavior

The module owns no durable local state. It models remote persistent state in the Windows registry: create, delete, set-value, load, unload, restore, replace, save, flush, and security calls can mutate or persist remote registry keys and hives on the target host. Handles are remote context handles represented by `RPC_HKEY`; the caller is responsible for closing them. Local state is limited to transient request objects, retry buffer lengths, packed value byte strings, and unpacked return values.

## Dependencies and Integration Points

`rrp.py` depends on Impacket's NDR framework (`NDRCALL`, `NDRSTRUCT`, pointer and conformant-array classes), common DCE/RPC data types from `impacket.dcerpc.v5.dtypes`, `DCERPCException`, `system_errors`, `LOG`, and `uuidtup_to_bin`. It integrates with the wider Impacket DCE/RPC stack through the `OPNUMS` map and `MSRPC_UUID_RRP`, and with callers through helper names that mirror the protocol calls. Test and example consumers commonly bind over SMB named pipes and then use helpers to enumerate or change remote registry state.

## Risks and Edge Cases

Registry string handling is sensitive to null termination and Python text/bytes boundaries. `packValue()` has fallbacks for filesystem encoding, but callers that pass bytes where strings are expected can still hit type-dependent behavior. There is also a likely copy/paste hazard in QWORD handling: `REG_QWORD` and `REG_QWORD_LITTLE_ENDIAN` share the same numeric constant, so the first matching branch in `packValue()`/`unpackValue()` wins and the later big-endian-style branch is unreachable for that value. `hBaseRegQueryMultipleValues()` has an explicit TODO and a fixed 128-byte buffer, so large values can be truncated or fail without the adaptive retry logic used by single-value helpers. Security descriptor buffers use fixed defaults in helpers, notably 1024 bytes for `hBaseRegGetKeySecurity()`. Mutating helpers can alter or destroy remote registry state and require suitable access masks and remote privileges.

## Test Signals

Useful test signals include unit tests for `packValue()`/`unpackValue()` across all supported registry types, including null-termination behavior and byte/string inputs; mocked DCE/RPC tests that inject `ERROR_MORE_DATA` for query and enum helpers and verify resized retries; round-trip tests for `RPC_HKEY.isNull()` and request field population; integration tests against a Windows target or fixture service for open/query/set/delete flows; and negative tests for insufficient access, missing keys, oversized values, and malformed security descriptors.
