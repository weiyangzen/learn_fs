# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncHSWriter.hh

Purpose: writes handshake request messages asynchronously and supports replaying a previously sent message for handshake wait/retry behavior.

Important APIs/types: `Reset(Message*)`, `Replay()`, `HasMsg()`, `Write()`, and stages `WriteRequest`/`WriteDone`. It owns the outgoing message through `unique_ptr<Message>`.

Control flow/state: `Write()` sends the message through `Socket::Send`, returns on `suRetry`, then flushes with `Socket::Flash`. `Replay()` resets the message cursor to zero and returns to `WriteRequest` without replacing the owned message. Dependencies are socket, status, logging, and `XrdSysE2T` for error text. Risks: `Write()` assumes `outmsg` is non-null when called; replay depends on cursor-correct message reuse; flush errors are logged and returned. Test signals: partial send retry, successful flush, replay after kXR_wait, and null-message guarding in callers.
