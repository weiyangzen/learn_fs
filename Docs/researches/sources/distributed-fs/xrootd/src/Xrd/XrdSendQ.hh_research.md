# sources/distributed-fs/xrootd/src/Xrd/XrdSendQ.hh

## Purpose

`XrdSendQ.hh` declares `XrdSendQ`, an `XrdJob` subclass that buffers socket output for an `XrdLink` when immediate nonblocking sends cannot finish. The file was read completely.

## Important APIs, Types, and Functions

Public methods are `Backlog()`, `DoIt()`, contiguous and iovec `Send()` overloads, static setters `SetAQ()`, `SetQM()`, `SetQW()`, and `Terminate()`. The constructor binds the queue to a link and write mutex. Private methods include `SendNB()`, `QMsg()`, `RelMsgs()`, and `Scuttle()`. The nested `mBuff` struct is a variable-length heap message node.

## Control Flow

The header establishes the contract that callers hold `wMutex` for `Send()` and `Terminate()`. `DoIt()` is invoked by `XrdScheduler` when queued data needs draining. Queue state and deletion are coordinated through `active` and `terminate`.

## State and Persistence Behavior

All state is process memory. Static fields define global warning and maximum queue policy. Per-link fields keep FIFO message pointers, deletion queue, fd, backlog count, warning escalation, discard count, and lifecycle flags. No durable state is present.

## Dependencies and Integration Points

It depends on `XrdJob`, `XrdLink`, `XrdSysMutex`, POSIX `unistd.h`, and `struct iovec`. It is part of the Xrd network/link send path and integrates with the global scheduler at implementation time.

## Risks and Edge Cases

The destructor is private and virtual, requiring lifetime to be controlled by `Terminate()` or internal self-deletion. The class exposes `Backlog()` without locking, so it is advisory. `SetAQ()` exposes `qPerm`, but this member has no observed use in the implementation, suggesting a stale or externally consumed policy hook.

## Test Signals

Compile coverage should catch ownership and include-order regressions. Runtime tests should validate that callers can safely use both send overloads under the write mutex and that `Terminate()` does not leak queued messages.
