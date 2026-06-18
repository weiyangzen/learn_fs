# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiAlert.cc

## Purpose
Implements pooled SSI alert callback objects used to return asynchronous attention/alert metadata to requestors.

## Important APIs, Types, And Functions
- Static pool members `aMutex`, `free`, `fNum`, and `fMax`.
- `XrdSsiAlert::Alloc()` obtains an alert object from the pool or allocates a new one and binds it to an `XrdSsiRespInfoMsg`.
- `Done()` deletes callback error info and recycles the alert.
- `Recycle()` releases the response message and returns the alert object to the bounded pool.
- `SetInfo()` formats an alert response into an `XrdOucErrInfo` message buffer as an iovec response containing `XrdSsiRRInfoAttn`.

## Control Flow
Allocation locks the pool, pops a free object if available, unlocks, clears `next`, and records `theMsg`. When the async callback completes, `Done()` deletes the callback-owned `XrdOucErrInfo` and calls `Recycle()`. Recycle calls `theMsg->RecycleMsg()` if present, then either deletes the alert if the pool is full or pushes it onto the free list. `SetInfo()` uses the existing error-info message buffer to build an iovec array: one slot for framework framing, one for the attention header, and one for alert payload.

## State And Persistence
Maintains a process-local bounded free list of alert objects, default max 100. Alert payload ownership belongs to `XrdSsiRespInfoMsg` and is released via `RecycleMsg()`. No alert data is persisted.

## Dependencies And Integration Points
Depends on `XrdOucErrInfo`, `XrdSsiAlert.hh`, and `XrdSsiRRInfo.hh`. Implements `XrdOucEICB` callback behavior used by SSI request/response paths.

## Risks And Edge Cases
- `SetInfo()` copies debug bytes with `sizeof(aMsg)`, but `aMsg` is a pointer, so this is pointer-size rather than caller-buffer-size based.
- `SetInfo()` assumes the error-info message buffer is large enough for `AlrtResp`.
- Pool state is protected by `XrdSysMutex`, but `theMsg` is not cleared before pooling, so reuse depends on `Alloc()` always resetting it.
- `Done()` always deletes `eiP`; callers must allocate it accordingly.

## Test Signals
Test pool reuse and max-size trimming, `RecycleMsg()` invocation, iovec/header formatting including network byte order, callback ownership of `XrdOucErrInfo`, and alert payload lengths including zero and large messages.
