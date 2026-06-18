# sources/distributed-fs/xrootd/src/XrdCl/XrdClTaskManager.hh

## Purpose

This header declares `Task`, the scheduled-work interface, and `TaskManager`, a simple one-thread delayed task scheduler used by client infrastructure.

## Important APIs, Types, and Functions

`Task::Run(time_t now)` returns zero to complete or a timestamp for rerun. Tasks also carry a name for logging. `TaskManager` exposes `Start`, `Stop`, `RegisterTask`, `UnregisterTask`, and `RunTasks`. Private `TaskHelper` stores task pointer, execution time, and ownership; `TaskHelperCmp` orders scheduled tasks.

## Control Flow

Clients register tasks with a target execution time. The manager thread repeatedly scans due tasks, runs them, reinserts rescheduled tasks, and deletes owned completed tasks. Unregistration requests are queued for the runner loop to process.

## State and Persistence Behavior

The manager keeps scheduled tasks and unregister requests in memory. Ownership is explicit per registration. There is no persistence or cross-process coordination.

## Dependencies and Integration Points

It depends on C time containers, pthread IDs, and `XrdSysMutex`. It is used by stream/postmaster logic for delayed reconnect and can support other short client tasks.

## Risks and Edge Cases

The header warns that one task can interfere with another because only one worker thread exists. Long tasks block all later scheduled work. The API does not return cancellation completion or registration handles, so pointer identity is the only unregister key.

## Test Signals

Compile-time signals should verify subclassing `Task`; runtime tests should validate owned versus non-owned deletion, reschedule timestamps, and unregister semantics.
