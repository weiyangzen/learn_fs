# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioTask.cc

Purpose: implements common async task behavior for file-to-link reads and link-to-file writes. It coordinates completed AIO buffers, waits for outstanding operations, handles disconnects, validates read ordering, and maps filesystem/protocol errors to client responses.

Important APIs and functions: `Completed()` is called by AIO buffers and queues completions on `pendQ`, waking a waiting task or rescheduling an offline one. `getBuff()` returns the next completed buffer, optionally waiting via `Wait4Buff()`. `Drain()` recycles completed buffers while waiting briefly for in-flight requests, then marks the task offline/done. `gdDone()` and `gdFail()` implement network get-data callbacks for link-to-file writes. `SendError()` and `SendFSError()` log and send mapped xrootd errors. `Validate()` handles negative AIO results, short reads, zero-length EOF, embedded short blocks, and high-offset tracking.

Control flow and state: `aioMutex` protects `pendQ`, `Status`, and wait transitions. `inFlight` and `isDone` are atomic because completions can arrive from filesystem threads. `Status` cycles through `Running`, `Waiting`, and `Offline`. `finalRead` stores the one allowed short read; `pendWrite` stores a write buffer awaiting full network delivery.

Dependencies and integration: derives from `XrdJob` and implements `XrdXrootdProtocol::gdCallBack`. It uses `XrdScheduler`, `XrdXrootdResponse`, `XrdSfs` errors, `XrdXrootdAioFob`, `XrdXrootdFile`, and trace/error logging.

Risks and test signals: the most fragile areas are races between client failure, queued completions, and task recycle; timeout behavior in `Wait4Buff()`; and EOF validation for parallel reads. Tests should cover short reads at end-of-data, embedded zero blocks, AIO errors, link abort during read and write, drain with tardy completions, and ensuring `Recycle(true)` only happens after references are safe.
