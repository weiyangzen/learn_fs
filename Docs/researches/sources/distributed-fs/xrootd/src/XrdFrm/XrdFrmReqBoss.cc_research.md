## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmReqBoss.cc

Purpose: implements a request-boss worker for one request persona (`pstg`, `migr`, `getf`, or `putf`). It persists client requests in priority queue files, drains them in priority order, and hands executable requests to `XrdFrmXfrQueue`.

Important APIs and control flow: `Start()` creates queue directories and `XrdFrcReqFile` objects for each priority, then starts the processing thread. `Add()` clamps request priority, stamps add time, appends to the proper request file, and wakes the thread. `Del()` cancels matching request IDs from all priority files. `Process()` waits via `Wakeup(0)`, then scans priorities high-to-low; each priority drains up to `i+1` pulls, registering cluster IDs or enqueueing transfers. `Register()` interprets request ID as a PID and stores cluster identity in `CID`.

State and persistence: `rQueue[]` is backed by request files under the queue path; `rqReady` and `isPosted` implement a binary semaphore to avoid wakeup storms. Registered cluster identity persists in the `CID` facility.

Dependencies and integration: used by `XrdFrmXfrDaemon` bosses. It depends on `XrdFrcReqFile`, `XrdFrcRequest`, `XrdFrmXfrQueue`, `XrdFrcCID`, and `XrdFrcUtils`.

Risks and test signals: queue fairness is weighted by priority and may starve lower priorities under continuous high-priority load. `Wakeup()` uses a static mutex shared across all bosses. Tests should cover restart persistence, cancellation, priority clamping, register request deletion on `CID.Add()` failure, and behavior when transfer queue rejects a request.
