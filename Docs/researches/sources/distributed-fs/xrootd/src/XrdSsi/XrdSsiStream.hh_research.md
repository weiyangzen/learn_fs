# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiStream.hh

## Purpose
`XrdSsiStream.hh` declares the stream abstraction used when an SSI response cannot or should not be sent as one direct data buffer. Streams may be active, where the producer supplies buffers, or passive, where the framework/client supplies buffers to fill.

## Important APIs and Types
Nested `Buffer` contains a data pointer, next pointer, and pure virtual `Recycle`. Stream methods are `GetBuff` for active streams, asynchronous `SetBuff(XrdSsiErrInfo&, char *, int)` for passive client-side streams, synchronous `SetBuff(XrdSsiErrInfo&, char *, int, bool&)` for passive streams, and `Type`. `StreamType` has `isActive` and `isPassive`.

## Control Flow
A responder posts a stream with `XrdSsiResponder::SetResponse(XrdSsiStream*)`. Server-side active streams return `Buffer` objects until `last` is true; receivers recycle each buffer. Passive streams fill caller-provided buffers either synchronously or by scheduling a callback to `ProcessResponseData`.

## State and Persistence
The base stores only the immutable stream type. Implementations own all buffer queues, file handles, or generated data. No persistence is defined by the interface.

## Dependencies and Integration Points
It depends on `XrdSsiErrInfo` and errno constants. `XrdSsiResponder`, `XrdSsiRequest`, and endpoint task/file-session code use this abstraction to transfer large or incremental responses.

## Risks and Test Signals
Default methods set `EOPNOTSUPP`, so implementations must override the correct method for their stream type. Tests should cover active buffer recycle, passive sync EOF/error semantics, async scheduling errors, `last` handling, type mismatches, and large responses that cross the direct-transfer threshold.
