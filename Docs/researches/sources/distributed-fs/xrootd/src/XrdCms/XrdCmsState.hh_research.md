# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsState.hh

## Purpose

`XrdCmsState` is the cluster-manager state publisher for CMS/olbd state. The header declares a process-global state object (`XrdCms::CmsState`) that tracks whether a server or front-end is suspended, whether staging is disabled, the data port, active subscriber counts, staging-capable subscriber counts, and manager/front-end/space health. Its public API is intentionally small because the implementation is used by protocol and monitor code to report state transitions to redirectors and subscribers.

## Important APIs and Types

The core state API is `Enable()`, `Monitor()`, `Port()`, `sendState(XrdLink *)`, two `Set()` overloads, and `Update(StateType, int, int)`. `StateType` distinguishes updates for aggregate activity, subscriber counts, front-end state, free-space state, and staging state. The public constants `SRV_Suspend`, `FES_Suspend`, `All_Suspend`, and `All_NoStage` encode state-control bits likely transmitted in CMS state messages or derived from admin files.

## Control Flow

Callers initialize thresholds and admin paths with `Set()`, enable reporting, then call `Update()` as cluster conditions change. `Status()` is private and computes the outbound status byte from state-change flags and current state. `Monitor()` is exposed as a thread entry point or long-running watcher that observes state changes and admin-control files; `sendState()` writes the current state to an `XrdLink`.

## State and Persistence Behavior

State is process-local but guarded by `XrdSysMutex` and signaled with `XrdSysSemaphore`, indicating concurrent producer/consumer updates. Persistence is indirect through `NoStageFile` and `SuspendFile` paths, which allow admin state to be represented by filesystem sentinels. The class tracks current and previous state to report changes only when meaningful.

## Dependencies and Integration Points

It depends on `XrdSys` threading primitives, `XrdCmsTypes.hh`, and `XrdLink`. It integrates with CMS configuration/protocol code that maintains subscriber counts and sends state to manager or redirector peers.

## Risks and Edge Cases

The interface exposes mutable `Suspended` and `NoStaging` fields, so callers can bypass the mutex if they write directly. Correct behavior depends on the unseen implementation consistently locking around all state transitions and respecting admin file state. Off-by-one or stale `minNodeCnt`/subscriber counts can incorrectly suspend a cluster.

## Test Signals

Useful tests would drive `Set()`, `Update()`, and admin-file changes while asserting state bytes emitted by `sendState()`, port reporting, and semaphore wakeups. Concurrency tests should stress simultaneous count, space, and staging updates.
