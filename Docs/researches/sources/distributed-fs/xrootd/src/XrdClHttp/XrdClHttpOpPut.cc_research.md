# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpPut.cc

## Purpose
`XrdClHttpOpPut.cc` implements `CurlPutOp`, the streaming HTTP upload operation used by `File::Write` and close-created zero-byte objects.

## Important APIs and Functions
Constructors accept either a non-owned buffer view or an owned `XrdCl::Buffer`. `Setup` enables upload, installs read callback/data, and sets object size when known. `ReadCallback` feeds libcurl from `m_data`, pauses when more client data is needed, and returns 0 when final. `Pause` reports successful consumption of the current chunk. `Continue` updates handler and buffer data, marks final on zero-size continuation, and queues the op on the continue queue. `ContinueHandle` unpauses curl. `Fail`, `Success`, and `ReleaseHandle` manage callbacks and curl option cleanup.

## Control Flow
`File::Write` creates one `CurlPutOp` at offset zero. Each subsequent sequential write calls `Continue`; when libcurl asks for data and none is available, `Pause` invokes the active handler and waits for the next continuation. `Close` finalizes by queueing a zero-size continuation.

## State and Persistence
The operation writes the remote object. It stores current curl handle, continue queue, optional owned buffer, non-owned data view, default error handler, offset/object-size fields, and final flag.

## Dependencies and Integration Points
It depends on libcurl upload callbacks, `HandlerQueue`, `File::PutResponseHandler`, connection/header callouts, and base `CurlOperation` timeout/error logic.

## Risks and Test Signals
The owned-buffer constructor initializes `m_data` from the moved-from parameter rather than `m_owned_buffer`, which deserves focused testing. Other risks are non-owned buffer lifetime, pause/resume races, zero-size final writes, and handle reuse. Tests should cover chunked PUT, buffer and raw-pointer overloads, final flush, failure with no active handler, continue-queue exceptions, and content-length injection via header callout.
