# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiSessReal.hh

## Purpose
`XrdSsiSessReal.hh` declares the client-side endpoint session object for SSI. It is both a session state holder and an `XrdSsiEvent` callback receiver for endpoint file open/close completions.

## Important APIs and Types
Public methods include `InitSession`, `Provision`, `Run`, `TaskFinished`, `UnHold`, `Unprovision`, `XeqEvent`, `GetKey`, `GetSID`, `SetKey`, `Lock`, `UnLock`, and `MutexP`. `epFile` is public because tasks need endpoint I/O access. Private helpers create/release tasks and handle shutdown.

## Control Flow
The header exposes a state machine: provision opens the endpoint, `XeqEvent` transitions out of open state and sends queued tasks, task completions decide whether to unprovision, and unhold removes reusable state.

## State and Persistence
The object stores endpoint and task state only in memory. The reusable resource key is duplicated and freed locally. `sessID` and `nextTID` identify sessions/tasks within the process, not across restarts.

## Dependencies and Integration Points
It depends on `XrdCl::File`, SSI atomics/events, SSI mutexes, `XrdSsiServReal`, and `XrdSsiTaskReal`. It is owned and recycled by `XrdSsiServReal`.

## Risks and Test Signals
The class relies on callers knowing when methods return with `sessMutex` unlocked or the object invalidated. Tests should inspect unprovision paths, free-task reuse when held, no-reuse marking, cleanup job behavior, and public `epFile` access under task concurrency.
