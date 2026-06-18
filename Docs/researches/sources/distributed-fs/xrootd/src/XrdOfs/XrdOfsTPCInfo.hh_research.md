# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCInfo.hh

## Purpose

`XrdOfsTPCInfo.hh` declares the TPC metadata object embedded in every `XrdOfsTPC`. It is the shared storage contract for rendezvous auth and destination copy jobs.

## Important APIs, Types, and Functions

Public methods include `Engage`, `Fail`, `isDest`, `Match`, `Reply`, `Set`, `SetCB`, `SetCreds`, `SetRPath`, `SetStreams`, and `Success`. Public data members include `cbP`, `Cks`, `Key`, `Org`, `Lfn`, `Dst`, `Spr`, `Tpr`, `Rpx`, credential environment/name/data fields, stream count, and state booleans `inWtR`, `isDST`, `isAOK`.

## Control Flow

The header exposes a deliberately direct data model. Callers populate the object during authorization or job creation, mark callbacks as engaged during async waits, and mark success when the transfer completes.

## State and Persistence Behavior

All string/credential data is heap-owned by the object except `Env`, which points to an environment-variable name. Persistence is process-memory only. Destination cleanup behavior is driven by `isDST` and `isAOK`.

## Dependencies and Integration Points

The header includes `XrdOucCallBack.hh` and forward-declares error and mutex types. It is included by `XrdOfsTPC.hh`, making it central to OFS TPC state layout.

## Risks and Edge Cases

Most members are public, so invariants are convention-based rather than enforced by accessors. `Engage()` must be called under a serialization lock per the comment. Public raw pointers increase risk when adding reuse paths.

## Test Signals

Compile and lifecycle tests should exercise construction with optional fields, `Set()` replacement, callback ownership, credential ownership, and destructor cleanup with all optional pointers populated.
