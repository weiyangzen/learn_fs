# sources/distributed-fs/xrootd/src/XrdSciTokens/XrdSciTokensMon.hh

## Purpose

`XrdSciTokensMon.hh` declares the small monitoring mixin used by the SciTokens authorization plugin.

## Important APIs, Types, And Functions

- `Mon_isIO(oper)` returns true for read, update, create, and exclusive create operations.
- `Mon_Report(Entity, subject, username)` emits token monitoring data.

## Control Flow

`XrdAccSciTokens` calls `Mon_isIO()` after successful scope-based authorization and calls `Mon_Report()` only for monitored I/O operations.

## State And Persistence

The class owns no state.

## Dependencies And Integration Points

It includes `XrdAcc/XrdAccAuthorize.hh` for `Access_Operation` and forward-uses `XrdSecEntity` through the implementation. It is a base class of `XrdAccSciTokens`.

## Risks And Edge Cases

- The monitored operation set is hard-coded; mkdir, rename, delete, stage, and poll are not reported by this helper.
- The header typo in its comment/name banner has no runtime effect.

## Test Signals

Unit tests should assert `Mon_isIO()` truth table for every `Access_Operation` and verify the implementation is called only for those operations.
