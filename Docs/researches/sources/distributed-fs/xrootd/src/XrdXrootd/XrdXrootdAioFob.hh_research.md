# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioFob.hh

Purpose: declares `XrdXrootdAioFob`, the queue manager used to order AIO tasks per protocol stream/path. It is a small synchronization and scheduling helper, not an I/O implementation itself.

Important APIs and types: public methods are `Reset()`, `Reset(XrdXrootdProtocol*)`, `Schedule(XrdXrootdAioTask*)`, and `Schedule(XrdXrootdProtocol*)`. Internal `AioTasks` stores `first` and `last` pointers for each per-stream queue. `Running[]` tracks whether a stream currently has a scheduled task. `maxQ` bounds reset scanning to streams that have been used.

Control flow and state: all queue mutation is protected by `fobMutex`. The task class is a friend only indirectly through public scheduling; the linked-list node is `XrdXrootdAioTask::nextTask`. The destructor calls `Reset()` so queued tasks do not leak when the owning file is closed.

Dependencies and integration: includes `XrdXrootdProtocol.hh` for `maxStreams` and path-id semantics, plus `XrdSysPthread` for the mutex. Owned by `XrdXrootdFile` and used by AIO task implementations.

Risks and test signals: the fixed array assumes protocol path ids are stable and bounded. Tests should check destructor cleanup, queue tail updates after dequeue, and handling of reset when `maxQ` is lower than `maxStreams`.
