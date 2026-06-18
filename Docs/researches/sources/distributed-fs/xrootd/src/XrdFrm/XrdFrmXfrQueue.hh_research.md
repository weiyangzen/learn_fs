## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrQueue.hh

Purpose: declares the static transfer queue service shared by request bosses, migration scanner, and transfer workers.

Important APIs/types: `Add()` enqueues a request, `Get()` blocks until a matching job is available, `Done()` completes a job, `Init()` sets up pools and stop monitors, and `StopMon()` is the monitor thread entry. Queue selection constants distinguish inbound-only, outbound-only, and any queue workers. Private `theQueue` stores semaphores, free and pending lists, stop-file metadata, and queue identity.

State and persistence: static hash `hTab` suppresses duplicates; `xfrQ[]` stores in-memory queues and free lists; request-file and notification persistence are handled by implementation collaborators.

Dependencies and integration: includes request, hash, and thread primitives; forward declares request files and jobs. `XrdFrmTransfer::Init()` must call `Init()` before workers call `Get()`.

Risks and test signals: all methods are static, so test isolation requires explicit process or state reset. Verify queue array sizing against `XrdFrcRequest::numQ` and stop-file naming conventions.
