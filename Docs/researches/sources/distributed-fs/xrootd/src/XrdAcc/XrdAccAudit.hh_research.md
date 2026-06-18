# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccAudit.hh

## Purpose

`XrdAccAudit.hh` declares the audit policy enum and default audit base class for authorization decisions. The file was read completely.

## Important APIs, Types, and Functions

`XrdAccAudit_Options` defines `audit_none`, `audit_deny`, `audit_grant`, and `audit_all`. `XrdAccAudit` exposes `Auditing()`, virtual `Deny()` and `Grant()`, `setAudit()`, and a constructor receiving `XrdSysError`. `XrdAccAuditObject()` is the external factory.

## Control Flow

The access engine queries `Auditing()` to decide whether a fast privilege test is enough or whether an audit call is needed. Implementations override `Grant()`/`Deny()` to route records elsewhere.

## State and Persistence Behavior

The class stores an option mask and message destination pointer. No persistent audit store is defined by the interface.

## Dependencies and Integration Points

It forward-declares `XrdSysError` and is used by `XrdAccAccess` and `XrdAccConfig`'s `acc.audit` directive. The comments document replacement by site-specific shared libraries.

## Risks and Edge Cases

The default implementation is intentionally minimal and not sufficient for strict audit requirements. `Auditing(ops)` returns a bitwise intersection, so callers must pass the right mask for their decision.

## Test Signals

Compile tests should cover subclass replacement. Functional tests should validate option parsing and that `Audit()` calls are made only under configured modes.
