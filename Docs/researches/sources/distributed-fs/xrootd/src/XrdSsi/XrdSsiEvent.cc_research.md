# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiEvent.cc

Purpose: implements asynchronous client-response event serialization for SSI objects that are both `XrdCl::ResponseHandler`s and scheduler jobs. It converts network callbacks into scheduler-executed `XeqEvent()` calls while preserving event order.

Important APIs and control flow: `AddEvent()` locks `evMutex`, records the first event in `thisEvent`, schedules the job if not running, and appends later events using pooled `EventData` nodes. `DoIt()` repeatedly moves the pending list into a local copy, unlocks, calls virtual `XeqEvent()` for each event, clears consumed events, and finally calls `XeqEvFin()`. Positive `XeqEvent()` return flushes normally; zero continues; negative halts because the object became invalid. `ClrEvent()` deletes status/response payloads and recycles chained nodes.

State and persistence: state is in-memory queue data: `thisEvent`, `lastEvent`, `running`, `isClear`, and static `freeEvent`, protected by `evMutex` plus static `frMutex`. No persistence occurs.

Dependencies and integration: depends on `XrdCl` response objects, `XrdScheduler`, and SSI tracing/mutex utilities. It is suitable for client-side service implementations that need ordered callback handling without executing complex code in the network callback thread. Risks include object deletion during `XeqEvent()`, correctness of event ownership/deletion, and pooled `EventData` reuse. Test signals should stress multiple queued callbacks, destructor cleanup with pending events, `XeqEvent()` return-code behavior, and scheduler single-run behavior.
