# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAudit.cc

## Purpose

`XrdAccAudit.cc` implements the default audit sink for authorization decisions. It logs grant/deny records to `XrdSysError` when audit options enable them and exposes a singleton factory. The file was read completely.

## Important APIs, Types, and Functions

The constructor initializes `auditops` to `audit_none` and stores the error destination. `Deny()` formats `"deny"` records when `audit_deny` is enabled. `Grant()` formats `"grant"` records. `XrdAccAuditObject()` returns a static `XrdAccAudit` instance.

## Control Flow

The access layer calls `Grant()` or `Deny()` after an operation test when configured auditing requires a record. Each method formats a bounded 2048-byte stack buffer and emits `mDest->Emsg("Audit", buff)`.

## State and Persistence Behavior

The default audit object is a process-lifetime static. Audit state is limited to the selected option mask and error destination pointer. Audit records persist only as far as the configured logging backend persists them.

## Dependencies and Integration Points

It integrates with `XrdAccAudit.hh` and `XrdSysError`. Sites can replace this default by providing a different audit object in a shared library.

## Risks and Edge Cases

`Grant()` checks `auditops & audit_deny`, not `audit_grant`; this appears to make grant-only auditing ineffective and grant logging dependent on deny auditing. The singleton captures the first `XrdSysError*` passed to the factory. Paths and identities are truncated at the fixed buffer size.

## Test Signals

Tests should verify deny-only, grant-only, all, and none audit modes. A grant-only test should catch the current gate mismatch. Logging tests should cover null trace identity and long path truncation.
