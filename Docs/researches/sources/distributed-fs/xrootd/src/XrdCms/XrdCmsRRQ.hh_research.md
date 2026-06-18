# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRRQ.hh

Purpose: declares the fast-response queue types used to coordinate redirector requests awaiting server/cluster results.

Important APIs/types: `XrdCmsRRQInfo` identifies a waiting request by cache key, stream id, redirector slot/instance, access mode, locate mode, response quorum, lookup options, interface preference, and rw server vector. `XrdCmsRRQSlot` stores one queued request plus piggyback chains. `XrdCmsRRQ` exposes `Add`, `Del`, `Init`, `Ready`, `Respond`, `Statistics`, and `TimeOut`, plus `Info` counters.

Control flow: callers add slots and later call `Ready()` when server masks are known; background threads perform response and timeout work.

State and persistence: fixed-size slot pool (`numSlots=1024`), wait/ready queues, response iovecs/templates, shared buffers, counters, timeout configuration, and semaphore/mutex synchronization.

Dependencies/integration: includes protocol integer types, CMS masks, `XrdOucDLlist`, and pthread wrappers. Exports global `XrdCms::RRQ`.

Risks: public statistics are snapshot-copied under lock but per-interval counters are folded in the responder. Fixed buffer sizes (`hostbuff[288]`, locate data from `RHLen*STMax`) must match formatter output. Static slot free list is separate from queue mutex, so lock ordering must remain stable.

Test signals: compile coverage when `STMax` or locate response size changes, concurrency tests for add/ready/timeout/recycle, and stats reset/reporting tests.
