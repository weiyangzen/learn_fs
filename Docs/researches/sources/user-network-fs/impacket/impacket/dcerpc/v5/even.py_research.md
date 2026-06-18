# sources/user-network-fs/impacket/impacket/dcerpc/v5/even.py

## Purpose

`even.py` implements the legacy [MS-EVEN] EventLog Remoting Protocol interface. It models RPC calls for opening event logs or backup logs, reading event records, clearing and backing up logs, registering event sources, reporting events, and querying record counts.

## Important APIs, Types, And Functions

The module exports `MSRPC_UUID_EVEN`, `DCERPCSessionError`, event type constants, read flags, size limits, and `EVENTLOG_HANDLE_W`. Important structures include `IELF_HANDLE`, raw packet `EVENTLOGRECORD`, `EVENTLOG_FULL_INFORMATION`, `RPC_CLIENT_ID`, and `RPC_STRING`.

RPC call classes cover opnums 0, 1, 2, 4, 5, 7, 8, 9, 10, and 11: `ElfrClearELFW`, `ElfrBackupELFW`, `ElfrCloseEL`, `ElfrNumberOfRecords`, `ElfrOldestRecord`, `ElfrOpenELW`, `ElfrRegisterEventSourceW`, `ElfrOpenBELW`, `ElfrReadELW`, and `ElfrReportEventW`. `OPNUMS` maps these calls. Helpers include `hElfrOpenBELW`, `hElfrOpenELW`, `hElfrCloseEL`, `hElfrRegisterEventSourceW`, `hElfrReadELW`, `hElfrClearELFW`, `hElfrBackupELFW`, `hElfrNumberOfRecords`, and `hElfrOldestRecordNumber`.

## Control Flow

Helpers create request objects, set handles and parameters, then call `dce.request()`. Open helpers set `UNCServerName` to `NULL` and protocol version to 1.1. `hElfrReadELW` defaults to seek plus forward reading from offset 0 and `MAX_BATCH_BUFF` bytes. `EVENTLOGRECORD` parsing is offset-driven, with fixed headers, null-terminated source/computer names, optional SID, string area, data payload, padding, and trailing length.

## State And Persistence Behavior

Local state is transient, but remote state can be modified. Clear, backup, and report operations can clear logs, create backup files, or add events. Open calls return server context handles that callers must close. The module does not track handle lifecycle automatically.

## Dependencies And Integration Points

Dependencies include Impacket NDR primitives, common dtypes, `lsad.PRPC_UNICODE_STRING_ARRAY`, `Structure`, NT error tables, UUID helpers, and `DCERPCException`. It integrates with Windows Event Log RPC endpoints and is used by remote administration, event collection, and tests.

## Risks And Edge Cases

Clear, backup, and report operations have side effects and may require privileges. Helpers accept default empty handles and do not validate handle provenance. `EVENTLOGRECORD` can misparse malformed or truncated buffers if offsets and lengths are inconsistent. `RPC_STRING` length handling should be checked for unusual non-byte text inputs.

## Test Signals

Tests should verify request opnums, version fields, defaults, and handle placement. `EVENTLOGRECORD` tests need captured records with and without SIDs, multiple insertion strings, data payloads, and padding. Integration tests should open a known log, query counts, read records, and close the handle; side-effect calls should run only in isolated environments.
