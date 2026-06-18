## sources/distributed-fs/xrootd/src/XrdSys/XrdSysLogging.cc

Purpose: implements remote/plugin log forwarding and base logger configuration.

Important APIs/types/functions: `XrdSysLogging::Configure()` configures local file output, plugin callback, sync/async mode, buffer allocation, and forwarding thread. `Forward()` sends or enqueues messages. Private `CopyTrunc`, `EMsg`, `getMsg`, and `Send2PI` support truncation, errors, ring-buffer queueing, and async delivery.

Control flow: configuration optionally binds the local logger, then if a plugin exists either sets synchronous forwarding when buffer size is zero or allocates a page-aligned queue buffer and starts `Send2PI`. `Forward()` computes message length; sync mode copies/truncates into an 8 KiB stack buffer and calls the plugin directly. Async mode locks `msgMutex`, drops too-long or no-room messages into a lost count, writes `MsgBuff` headers and text into a circular buffer, posts `msgAlert` when the queue transitions from empty, and returns whether local logging should stop. `Send2PI()` waits, drains queued messages, and synthesizes lost-message notices.

State and persistence: module-static queue pointers, plugin function pointer, semaphore, mutex, lost-message counters, mode flags, and forwarding thread id. No disk persistence except through configured local logger.

Dependencies and integration: uses `XrdSysLogger`, `XrdSysLogPI`, `XrdSysThread`, `XrdSysSemaphore`, `posix_memalign`, and `getpagesize`.

Risks: async queue has bounded capacity and drops messages. `logDone` suppresses local output when only remote output is configured. The forwarding thread runs indefinitely. Plugin callbacks must tolerate message lifetime only during the call.

Test signals: local-only, remote-only, local+remote, sync and async plugin modes, queue overflow/lost notices, oversized messages, plugin thread id/time arguments, and startup failure for allocation/thread creation.
