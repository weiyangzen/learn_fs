# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncMsgWriter.hh

Purpose: writes queued normal requests, optional transport signatures, and optional raw request bodies for a substream.

Important APIs/types: `Reset()`, `Write()`, stages `WriteStart`, `WriteSign`, `WriteRequest`, `WriteRawData`, and `WriteDone`. It obtains `(Message*, MsgHandler*)` from `Stream::OnReadyToWrite`, does not own the main message, and owns only the optional signature message.

Control flow/state: `WriteStart` selects a message and asks the transport for a signature. Subsequent stages send signature, request, raw body via `MsgHandler::WriteMessageBody`, flush the socket, and notify `Stream::OnMessageSent`. `suRetry` preserves cursor/stage state. Dependencies are transport, socket, stream, channel `AnyObject`, and logging. Risks: assumes a non-null `outhandler` when checking raw status, size accounting combines message/signature/raw bytes, and `ECONNRESET` handling is in the caller. Test signals: empty queue returns `suAlreadyDone`, signature path, raw-body partial writes, flush failure, and sent callback size.
