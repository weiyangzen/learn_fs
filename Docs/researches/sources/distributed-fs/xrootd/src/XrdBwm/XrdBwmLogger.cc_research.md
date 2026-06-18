# sources/distributed-fs/xrootd/src/XrdBwm/XrdBwmLogger.cc

Purpose: asynchronously emits BWM scheduling events to the server log, a FIFO/named socket, or an external collector program.

Important APIs/types/functions: local `XrdBwmLoggerMsg` message blocks; `XrdBwmLoggerSend` thread trampoline; constructor/destructor; `Event`, `sendEvents`, `Start`, `Feed`, `getMsg`, and `retMsg`.

Control flow: `Start` interprets target `*` as server log, `>path` as FIFO/socket path created by `XrdNetSocket`, otherwise sets up and starts an `XrdOucProg`. It then starts a sender thread. `Event` formats an XML-ish `<stats id="bwm">` message from `Info`, queues it, and posts a semaphore. `sendEvents` drains the queue and writes to the selected sink. Message blocks are recycled with a bounded in-flight cap.

State and persistence: persistent process state includes target string, program/socket fd, message queues, free pool, thread id, and queue counters. Events are not durably stored by this class; persistence depends on the sink.

Dependencies and integration points: uses XrdOucProg for collector programs, XrdNetSocket FIFO support, XrdSys threading/synchronization, and XrdSysError logging.

Risks: formatted XML has `<sz>%lld<sz>` instead of a closing `</sz>`, likely producing malformed messages. `Start` initializes `msgFD` to 0 in constructor, so destructor may close stdin if not started carefully. Queue overflow drops events with throttled warnings. Program feed blocking is isolated to sender thread but still can build queue pressure.

Test signals: target modes (`*`, `>socket`, program), queue overflow warning, sender thread shutdown, malformed XML regression, collector backpressure, and destructor resource cleanup.
