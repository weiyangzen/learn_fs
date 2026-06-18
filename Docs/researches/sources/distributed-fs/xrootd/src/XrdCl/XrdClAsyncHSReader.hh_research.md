# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncHSReader.hh

Purpose: reads handshake response messages asynchronously, preserving partial progress across poll events.

Important APIs/types: constructor binding transport, socket, stream name, stream, and substream; `Read()`, `ReleaseMsg()`, `Reset()`, and `Stage` values `ReadStart`, `ReadHeader`, `ReadMsgBody`, `ReadDone`.

Control flow/state: `Read()` loops its state machine until it must return, allocating a `Message`, asking `TransportHandler::GetHeader`, then `GetBody`, returning `suRetry` on partial socket progress. `ReleaseMsg()` transfers ownership and resets the stage. There is no persistence outside the in-flight `unique_ptr<Message>`. Dependencies are transport handler, socket, stream, status, and logging. Risks: callers must only release after a complete read; any transport framing bug propagates into handshake failure. Test signals: partial header/body retry, complete message release, reset reuse, and transport error propagation.
