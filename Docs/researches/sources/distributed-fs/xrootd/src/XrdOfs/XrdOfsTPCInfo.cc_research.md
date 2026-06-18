# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCInfo.cc

## Purpose

`XrdOfsTPCInfo.cc` implements the metadata container shared by TPC auth grants and transfer jobs. It owns copied rendezvous strings, destination paths, callback objects, forwarded credentials, checksum/protocol options, and cleanup behavior.

## Important APIs, Types, and Functions

Implemented methods are destructor, `Fail`, `Match`, `Reply`, `Set`, and `SetCB`. Inline setters and flags are declared in the header. `Set()` canonicalizes destination host names with `XrdNetAddr`; `Reply()` safely detaches and completes `XrdOucCallBack` objects.

## Control Flow

`Set()` replaces key/origin/LFN/destination/checksum fields and validates destination host resolution. `Match()` compares nullable key, origin, LFN, and destination fields exactly. `SetCB()` creates an async callback from `XrdOucErrInfo`; `Reply()` clears the callback pointer, optionally unlocks a passed mutex before invoking the callback, and only replies if `Engage()` marked the object as in wait-response state. `Fail()` formats a copy error and updates stats.

## State and Persistence Behavior

The object owns heap copies of strings and credentials and deletes its callback in the destructor. If marked as destination (`isDST`) and not successful (`isAOK`), the destructor can unlink the destination LFN when `Cfg.autoRM` is enabled. Callback state is one-shot: `Reply()` nulls `cbP` before unlocking or invoking user-visible completion.

## Dependencies and Integration Points

It integrates with `XrdOucCallBack`, `XrdOucErrInfo`, `XrdNetAddr`, `XrdOss` cleanup, `OfsEroute`, `XrdOfsStats`, and `XrdSfsInterface` return/error conventions. It is embedded in `XrdOfsTPC`, so all derived TPC objects inherit this state.

## Risks and Edge Cases

Host canonicalization can fail and reject otherwise plausible destination strings. `SetCreds()` overwrites `Crd` without freeing an existing value; current callers set it once, but reuse would leak. `Reply()` correctness depends on callers holding the appropriate serialization lock when passing `mP`.

## Test Signals

Tests should cover nullable field matching, destination canonicalization failures, callback reply with and without wait-response engagement, auto-remove destructor behavior, and failure-stat accounting.
