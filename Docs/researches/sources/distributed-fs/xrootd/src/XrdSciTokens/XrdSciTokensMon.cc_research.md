# sources/distributed-fs/xrootd/src/XrdSciTokens/XrdSciTokensMon.cc

## Purpose

`XrdSciTokensMon.cc` formats and emits security-monitoring token records for successful SciTokens-authenticated I/O.

## Important APIs, Types, And Functions

- `XrdSciTokensMon::Mon_Report(Entity, subject, username)` formats `s`, `n`, `o`, `r`, and `g` fields into a buffer and sends it to `Entity.secMon->Report(XrdSecMonitor::TokenInfo, buff)`.

## Control Flow

The method is called from `XrdAccSciTokens::Access()` after scoped authorization grants an I/O operation and `Mon_isIO()` indicates the operation should be monitored. It no-ops if `Entity.secMon` is null.

## State And Persistence

There is no local state. Monitoring records go to the configured `XrdSecMonitor` sink and are not persisted here.

## Dependencies And Integration Points

It depends on `XrdSciTokensMon.hh`, `XrdSecEntity`, and `XrdSecMonitor`. It integrates with the security monitoring channel and SciTokens authorization.

## Risks And Edge Cases

- Formatting uses a fixed 2048-byte stack buffer and truncates groups to 1024 characters.
- Field values are inserted without escaping in query-string-like format, so special characters in subject, username, issuer, role, or groups may affect downstream parsing.

## Test Signals

Tests should use a fake monitor to verify emission on configured entities, no-op without `secMon`, truncation behavior, and parsing of records containing empty issuer/role/group values.
