# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucCallBack.cc

## Purpose
Implements `XrdOucCallBack`, a wrapper that turns an `XrdOucErrInfo` callback capability into a controlled asynchronous reply sequence.

## Important APIs, Types, And Functions
`Cancel()` replies with retry semantics when a callback is outstanding. `Init(XrdOucErrInfo*)` captures the original callback object and argument, copies the user id, and replaces the input error-info callback with this wrapper. `Reply(int,int,const char*,const char*)` constructs a fresh `XrdOucErrInfo`, waits for the initial wait-for-callback notification, invokes the original callback's `Done`, and waits again for send completion.

## Control Flow
Initialization only succeeds when no callback is already pending and `eInfo` supplies a callback. Reply first atomically detaches `cbObj`, waits on `cbSync`, fills callback error text/code, calls the original callback, then waits for the wrapper `Done()` to post again. `Cancel` is just `Reply(1, 0, "")`, signaling retry.

## State And Persistence
State is transient: `cbObj`, `cbArg`, `UserID`, and semaphore `cbSync`. The object is deliberately not multi-thread safe and must be used serially. No persistent state is written.

## Dependencies And Integration Points
Depends on `XrdOucCallBack.hh`, `XrdOucErrInfo`, `XrdOucEICB`, and `XrdSysSemaphore`. It integrates with plugin/server flows where an operation returns an intermediate wait state and later completes asynchronously.

## Risks And Test Signals
The major risk is deadlock if `Init()` is called and neither `Reply()` nor `Cancel()` completes the two-semaphore protocol. Other risks are object reuse races and callbacks that never invoke the nested `Done`. Test signals include async completion ordering, destructor-triggered cancel, retry behavior, and callback clients that verify causality between wait notification and final reply.
