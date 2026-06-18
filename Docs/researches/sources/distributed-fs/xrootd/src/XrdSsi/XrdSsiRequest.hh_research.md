# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRequest.hh

Purpose: declares the abstract SSI request API used on both client and server sides. It is the core contract between service execution, responder posting, and client response consumption.

Important APIs/types: public API includes `Finished()`, `GetDetachTTL()`, `GetEndPoint()`, `GetMetadata()`, pure virtual `GetRequest()`, `GetRequestID()`, `GetResponseData()`, `GetTimeOut()`, pure virtual `ProcessResponse()`, optional `ProcessResponseData()`, and `ReleaseRequestBuffer()`. Protected hooks include `Alert()`, `RelRequestBuffer()`, `SetDetachTTL()`, `SetRetry()`, `SetTimeOut()`, and protected destructor. Private hooks `BindDone()`, `CleanUp()`, `CopyData()`, and `Dispose()` are used via friends.

Control flow and state: `XrdSsiResponder` and `XrdSsiRRAgent` are friends because they need to bind responders, set response info, set mutexes, and reset objects. Private state stores request ID, current mutex, responder pointer, `XrdSsiRespInfo`, `XrdSsiErrInfo`, endpoint, detach TTL, timeout, client/server marker, and flags.

Dependencies and integration: depends on SSI atomics, errors, and response info. It is subclassed by transport-specific request types such as `XrdSsiFileReq` and by client applications. Risks include strict lifecycle requirements: creator may delete only after `Finished()`/unbind, response buffers must remain valid until `Finished()`, and protected setters must be called before processing starts. Test signals should compile minimal subclasses and exercise response, alert, detach, retry, and buffer-release contracts.
