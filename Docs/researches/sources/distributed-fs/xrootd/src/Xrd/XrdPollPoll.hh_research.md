## sources/distributed-fs/xrootd/src/Xrd/XrdPollPoll.hh

Purpose: declares the portable `poll(2)` backend for platforms that do not use the Linux epoll implementation.

Important APIs/types/functions: public overrides `Disable`, `Enable`, and `Start`; protected `doDetach`, `Exclude`, and `Include`; private helpers `doRequests`, `dqLink`, `LogEvent`, `Recover`, and `Restart`. State includes `PollTab`, active count `PollTNum`, pending `PollQ`, `PollMutex`, and `maxent`.

Control flow: the common `XrdPoll` layer attaches links through `Include()`. The backend event loop waits on the poll table and command pipe, queues ready links, disables them during processing, and recovers/restarts after poll errors.

State/persistence: runtime-only poll table and queued link state.

Dependencies/integration: POSIX `poll`, `XrdPoll`, `XrdPollInfo`, and mutex support through the included common header.

Risks: `class XrdPollPoll : XrdPoll` uses private inheritance by default, unlike the public epoll backend; construction through `newPoller()` may still work internally, but external substitutability is limited. Poll table compaction and queued `XrdPollInfo` pointers must avoid stale references after link close.

Test signals: non-Linux CI should cover include/exclude, recovery after `poll()` errors, command processing limits, queue dequeue behavior, and restart logging.
