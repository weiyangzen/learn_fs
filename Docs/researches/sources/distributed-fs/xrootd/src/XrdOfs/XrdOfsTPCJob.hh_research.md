# sources/distributed-fs/xrootd/src/XrdOfs/XrdOfsTPCJob.hh

## Purpose

`XrdOfsTPCJob.hh` declares the destination-side copy-job subtype of `XrdOfsTPC`. It gives OFS a polymorphic object that can be synchronized, deleted, queued, and completed by transfer workers.

## Important APIs, Types, and Functions

Public methods are `Del`, `Done`, `Sync`, the constructor, and destructor. Private state includes global queue mutex/head/tail, per-job next pointer, assigned program, error code, `jobStat` enum (`isWaiting`, `isRunning`, `isDone`), and `lfnPos` rename bookkeeping.

## Control Flow

The header defines the job lifecycle used by `XrdOfsTPCJob.cc`: constructed by `XrdOfsTPC::Validate`, possibly started by `Sync`, completed by `XrdOfsTPCProg::Run`, and cleaned by OFS close paths.

## State and Persistence Behavior

State is in-memory only. Queue membership is represented by inherited `inQ` plus `Next`; lifetime is inherited reference counting.

## Dependencies and Integration Points

It includes `XrdOfsTPC.hh` and `XrdSysPthread.hh`, and forward-declares `XrdOfsTPCProg`. It is used by `XrdOfsTPC.cc` and `XrdOfsTPCProg.cc`.

## Risks and Edge Cases

The header exposes a small API, but lifecycle depends on private static queue invariants. `lfnPos` is set in the constructor but not consumed in the read implementation, so related behavior may depend on other build variants or legacy code.

## Test Signals

Compile tests should verify the derived object can be returned as `XrdOfsTPC *`. Lifecycle tests should validate status transitions and deletion in each state.
