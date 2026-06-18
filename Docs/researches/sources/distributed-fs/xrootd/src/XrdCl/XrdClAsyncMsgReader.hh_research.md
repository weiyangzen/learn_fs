# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncMsgReader.hh

Purpose: reads normal XRootD responses asynchronously and dispatches completed messages to the owning `Stream`.

Important APIs/types: `Reset()`, `Read()`, helper `ReadAttnActnum()`, `IsStatusRsp()`, `HasEmbeddedRsp()`, and stages for header, attention, more-body, message body, raw data, and completion. It uses `shared_ptr<Message>` because `MsgHandler` may share ownership.

Control flow/state: after reading a header, `kXR_attn` responses read an action code and may unwrap embedded async responses. Otherwise the stream can install an incoming handler for raw bodies. `kXR_status` may request raw or additional body reads through `InspectStatusRsp`. Completed messages call `strm.OnIncoming`. State persists as current stage, message, byte count, and handler across `suRetry`. Dependencies are transport, socket, stream, response structs, and logging. Risks: protocol boundary parsing, corrupted status handling, and shared ownership with handlers. Test signals: attention embedded response, status with raw/more data, partial socket retries, corrupted handler action, and final `OnIncoming` size.
