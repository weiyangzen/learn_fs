# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiTaskReal.hh

## Purpose

This header declares `XrdSsiTaskReal`, the concrete SSI task/responder/stream object used by real SSI sessions. It combines `XrdSsiEvent` callback execution, `XrdSsiResponder` response delivery, and `XrdSsiStream` passive streaming into one object owned by an `XrdSsiSessReal`.

## Important APIs, types, and functions

`TaskStat` models task lifecycle: pending, writing, waiting synchronously for response metadata, stream-ready, done, and dead. Public APIs include `Init`, `SetTaskID`, `SendRequest`, `Kill`, `Detach`, `Finished`, `SchedError`, `SendError`, `PostError`, `SetBuff` overloads for stream reading, `XeqEvent`, and `XeqEvFin`. `Implementation` returns the concrete object pointer for framework callbacks, `ID` returns the task id, and `RequestID` forwards to the bound request.

The object also exposes an intrusive doubly-linked `attList` node for session attachment lists. Private members keep error info, session/request pointers, retained metadata response ownership, pending write semaphore, stream buffers, status, task id, callback-defer count, timeout, and message-handler-pending state.

## Control flow

Callers initialize reusable task objects with `Init`, assign a task/session id with `SetTaskID`, then call `SendRequest`. From there the implementation file drives the asynchronous state machine through XrdCl callbacks and responder callbacks. Stream users interact through the two `SetBuff` overloads after a stream response has put the task in `isReady`.

## State and persistence behavior

The header defines only transient runtime state. `Init` resets request binding, state, timeout, `wPost`, `mhPend`, `defer`, attachment links, and any retained metadata response. The destructor deletes `mdResp` if present. No data is persisted beyond the lifetime of the task/session.

## Dependencies and integration points

The class inherits from SSI framework abstractions and references `XrdSsiRequest`, `XrdSsiSessReal`, `XrdSysSemaphore`, XrdCl response types, and SSI response/error/stream types. The interface is designed to be called from session management and XrdCl callback infrastructure rather than directly by plugins.

## Risks and edge cases

The class owns raw pointers and uses explicit lifetime conventions; copying would be unsafe and is implicitly avoided by normal usage. `RequestID` assumes `rqstP` is valid. `Init` deletes `mdResp`, so reinitialization while any upper-layer metadata/data pointer is still being used would be unsafe. The intrusive `attList` requires callers to preserve list invariants when moving tasks between session lists.

## Test signals

Header-level coverage comes from tests or integration runs that reuse a task object, bind it to a request/session, stream data through both `SetBuff` forms, and cancel at each state. ABI-sensitive checks should confirm enum values and inheritance remain compatible with callback dispatch users.
