# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiFileReq.hh

Purpose: declares the request object that bridges SSI service processing to the XRootD SFS file protocol. It packages request lifecycle, callback handling, scheduler execution, response draining, and object pooling.

Important APIs/types: inherits `XrdSsiRequest`, `XrdOucEICB`, and `XrdJob`. Public methods include `Activate()`, `Alert()`, static `Alloc()`, `DeferredFinalize()`, `Finalize()`, `GetRequest()`, `ProcessResponse()`, `Read()`, `RelRequestBuffer()`, `Send()`, `WantResponse()`, callback `Done()`, and job `DoIt()`. State enums `reqState` and `rspState` encode client delivery and responder binding state.

Control flow and state: private methods `BindDone()` and `Dispose()` override request hooks used by responder lifecycle. `Emsg()` variants format errors, `readStrmA/P()` and `sendStrmA()` handle stream response transfer, and `WakeUp()` invokes deferred response callbacks. Static members implement a free list. Instance fields track request/session pointers, callback info, alert queues, response offsets, request buffers, stream buffer, state flags, and compact textual request ID.

Dependencies and integration: depends on SFS XIO/DIO types, scheduler jobs, SSI request/responder/stream classes, and file-session/resource classes. Risks are ABI/lifecycle sensitive: callers must not delete pooled objects directly, callback fields must match pending `fctl()` state, and state enum transitions must remain compatible with the implementation. Test signals should assert all public paths leave objects recyclable and that `SetMax()` limits pool growth.
