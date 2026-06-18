<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdJob.hh -->
# sources/distributed-fs/xrootd/src/Xrd/XrdJob.hh

Purpose: declares the minimal abstract job base class used by `XrdScheduler` queues.

Important APIs/types/functions: public `NextJob`, `Comment`, pure virtual `DoIt()`, constructor, virtual destructor, private `SchedTime`, and friendship with `XrdScheduler`.

Control flow: scheduler code links jobs through `NextJob`, schedules by private `SchedTime`, and invokes `DoIt()` polymorphically when work is due. The class itself contains no scheduling logic.

State and persistence behavior: in-memory queue node state only. `Comment` is a static-description pointer for debugging, not owned text. `SchedTime` is managed by the scheduler.

Dependencies: standard C headers for allocation/string/time and no Xrd-specific includes by design; comments state it should remain independent for queue-processing efficiency.

Integration points: any component that wants scheduled work derives from `XrdJob` and implements `DoIt()`. `XrdScheduler` is the only class allowed to manipulate private schedule time.

Risks: derived jobs must manage their own lifetime and thread-safety. Public `NextJob` is optimized for queues but can be corrupted by accidental external writes. `Comment` must outlive the job if it points to static text as intended.

Test signals: scheduler unit tests with derived jobs; queue integrity tests; delayed execution tests; sanitizer tests for job lifetime and virtual destructor behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdJob.hh -->
