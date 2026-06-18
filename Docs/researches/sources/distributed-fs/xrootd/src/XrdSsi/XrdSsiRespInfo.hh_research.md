# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRespInfo.hh

Purpose: defines the SSI response payload representation and alert-message abstraction. It is used mainly by server-side responders and transport code to communicate response type, metadata, and payload handle.

Important APIs/types: `XrdSsiRespInfo` has response union fields for data buffer, error message, file size, or stream pointer; a second union for buffer length, errno, or file descriptor; metadata length/pointer; and `Resp_t` values `isNone`, `isData`, `isError`, `isFile`, `isStream`, and `isHandle`. `Init()` resets all fields, and `State()` returns a textual state. `XrdSsiRespInfoMsg` wraps alert messages with `GetMsg()` and pure virtual `RecycleMsg(bool sent)`.

Control flow and state: `XrdSsiResponder::SetResponse()` fills this structure, and request/session code interprets it to return direct data, stream data, file data, or errors. The structure borrows all payload pointers/file descriptors; ownership and lifetime are controlled by responder `Finished()`.

Dependencies and integration: forward-declares `XrdSsiStream` and is included by request/responder/table protocol code. Risks include union misuse when `rType` is wrong, missing ownership semantics for file descriptors/streams/buffers, `isHandle` being declared but not handled by all transport code, and metadata pointer lifetime. Test signals should cover every `Resp_t`, `Init()` reset, `State()` strings, alert recycling on sent/unsent paths, and responder-finished cleanup.
