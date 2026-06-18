# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsJob.hh

Purpose: declares `XrdCmsJob`, the `XrdJob` subclass used to run CMS protocol request execution on the scheduler and recycle job objects.

Important APIs/types/functions: `Alloc(XrdCmsProtocol*, XrdCmsRRData*)`, `DoIt()`, `Recycle()`, constructor, and private pool members `JobMutex`, `JobStack`, `JobLink`, `theProto`, and `theData`.

Control flow: the interface promises a lifecycle of allocate, schedule/execute, optionally reschedule, then recycle. `DoIt()` is the scheduler callback inherited from `XrdJob`.

State and persistence behavior: instances hold transient protocol and request data pointers. Static state holds a process-local freelist. There is no persistent state.

Dependencies: includes CMS protocol wire definitions indirectly through `YProtocol.hh`, `XrdJob`, and pthread mutexes. It forward-declares the protocol and RR data classes.

Integration points: used by `XrdCmsProtocol` and `XrdScheduler` as the async request work item for CMS connections.

Risks: raw pointers mean ownership is implicit and enforced only by implementation discipline. Copying is not disabled in the header, so accidental copies would be unsafe, though normal use allocates dynamically through `Alloc()`.

Test signals: compile integration with scheduler, pool reuse tests, and static analysis for copy misuse/reference lifetime.
