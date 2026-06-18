# sources/distributed-fs/xrootd/src/XrdAcc/XrdAccPrivs.hh

## Purpose

`XrdAccPrivs.hh` defines the authorization privilege bit masks, auth DB privilege characters, and positive/negative privilege accumulator used by XrdAcc. The file was read completely.

## Important APIs, Types, and Functions

`XrdAccPrivs` assigns bit masks for delete, insert, lock, lookup, rename, read, write, stage, poll, composites like chmod/chown/create/update, `All`, and `None`. `XrdAccPrivSpec` maps auth DB characters such as `a`, `d`, `i`, `k`, `l`, `n`, `r`, `w`, and `-`. `XrdAccPrivCaps` stores `pprivs` and `nprivs`.

## Control Flow

There is no executable flow. `XrdAccConfig::PrivsConvert()` parses privilege strings into `XrdAccPrivCaps`; `XrdAccCapability::Privs()` accumulates them; `XrdAccAccess::Access2()` computes `pprivs & ~nprivs`; `Test()` maps operations to required masks.

## State and Persistence Behavior

The file defines compile-time constants and a tiny stack/heap accumulator struct. No persistent state is owned.

## Dependencies and Integration Points

It is included by the authorization interface, capability engine, and config parser. Its bit assignments are an internal ABI for auth DB interpretation.

## Risks and Edge Cases

Composite masks must remain aligned with `Access_Operation` tests. Stage and poll masks exist here, but the observed `XrdAccAccess::Test()` table omits corresponding operation entries. Negative privilege strings can remove bits granted by unrelated matching capabilities.

## Test Signals

Tests should validate conversion of every privilege character, composites for each operation, negative privilege subtraction, and stage/poll authorization.
