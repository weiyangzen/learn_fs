# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdAioFob.cc

Purpose: implements a per-file async read freight/order buffer that serializes AIO task execution by xrootd stream/path id. It prevents multiple AIO tasks for the same protocol path from running concurrently while allowing different path ids to progress independently.

Important APIs and functions: `Schedule(XrdXrootdAioTask*)` either sends a task to the global `XrdScheduler` immediately or appends it to the per-path linked queue if that path is already running. `Schedule(XrdXrootdProtocol*)` is called when a task finishes and starts the next queued task for that protocol path. `Reset()` discards all queued work; `Reset(XrdXrootdProtocol*)` discards queued work for one path. `Notify()` provides trace messages with operation type, offset, length, and file key.

Control flow and state: `Running[pathID]` is the key state bit. Under `fobMutex`, a newly scheduled task sees either `Running == false` and becomes active, or joins `aioQ[pathID]`. Completion calls the protocol overload, which dequeues one item and schedules it or clears `Running`. Reset recycles queued tasks with `Recycle(true)` and marks paths idle.

Dependencies and integration: uses `XrdScheduler`, `XrdXrootdAioTask`, `XrdXrootdFile`, `XrdXrootdProtocol::getPathID()`, and tracing. It is owned from `XrdXrootdFile::aioFob` and is reset on file destruction or link failure.

Risks and test signals: path ids must remain within `XrdXrootdProtocol::maxStreams`. Task cancellation must not race with scheduler dispatch. Tests should exercise same-stream serialization, multi-stream parallelism, reset during queued work, and disconnect cleanup that calls `Reset(protP)`.
