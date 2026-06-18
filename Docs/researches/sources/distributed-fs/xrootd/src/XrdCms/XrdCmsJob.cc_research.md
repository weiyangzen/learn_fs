# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsJob.cc

Purpose: implements pooled scheduler jobs that execute a CMS protocol request asynchronously against an `XrdCmsProtocol` instance.

Important APIs/types/functions: static `XrdCmsJob::Alloc()`, `DoIt()`, and `Recycle()`, plus static pool state `JobMutex` and `JobStack`. It uses global `XrdCms::Sched`.

Control flow: `Alloc()` pops a job from `JobStack` under `JobMutex` or creates a new one, stores the protocol/data pointers, sets the scheduler comment to the protocol role, and increments the link reference. `DoIt()` calls `theProto->Execute(*theData)`. If execution returns `-EINPROGRESS`, it reschedules the same job for `theData->waitVal + time(0)`. Otherwise it releases the protocol reference and recycles. `Recycle()` decrements the link ref, objectifies/releases the RR data buffer, and pushes the job back on the free stack.

State and persistence behavior: state is an in-memory freelist of reusable job objects. Link/protocol references are used as lifetime guards while scheduled work is pending. No disk persistence.

Dependencies: `XrdScheduler`, `XrdJob`, `XrdLink`, `XrdCmsProtocol`, `XrdCmsRRData`, CMS tracing, and errno/time APIs.

Integration points: `XrdCmsProtocol` schedules request processing through these jobs when immediate inline handling is undesirable or a request must sleep and resume.

Risks: correctness depends on balanced protocol and link reference updates. A job rescheduled for `-EINPROGRESS` keeps the same data pointer and must not be recycled elsewhere. Allocation failure logs but leaves caller to handle null. The object pool never shrinks, matching daemon lifetime assumptions.

Test signals: unit tests with fake protocol returns for success, error, and `-EINPROGRESS`; reference-count assertions around `Alloc()`/`Recycle()`; scheduler tests verifying delayed reschedule; leak/race tests under concurrent allocation.
