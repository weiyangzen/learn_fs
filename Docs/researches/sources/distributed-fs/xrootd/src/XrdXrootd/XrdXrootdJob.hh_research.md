# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdJob.hh

Purpose: declares the keyed job scheduler used to execute external programs behind xrootd requests with concurrency limits and client wait semantics.

Important APIs/types/functions: option flags `JOB_Sync` and `JOB_Unique`; public methods `Schedule`, `Cancel`, `List`, and `DoIt`; constructor `XrdXrootdJob(XrdScheduler*,XrdOucProg*,const char*,int)`; private `CleanUp` and `sendResult`; `reScan` interval of 15 minutes.

Control flow: callers schedule by job key and argv vector, optionally requiring uniqueness or synchronous waiting. The object itself is also an `XrdJob` scheduled periodically to scan job/client state.

State and persistence behavior: maintains an `XrdOucTable<XrdXrootdJob2Do>`, a mutex, scheduler/program pointers, duplicated job name, maximum running jobs, and current job count. State is volatile and process-local.

Dependencies: `XrdJob`, `XrdOucProg`, `XrdOucTList`, `XrdOucTable`, `XrdSysPthread`, `XrdLink`, `XrdScheduler`, and `XrdXrootdResponse`.

Integration points: consumed by request handlers that need queued helper execution and by administrative list/cancel commands.

Risks: destructor notes there is no reliable deletion because unsynchronized worker threads may still reference the object. Consumers should treat instances as process-lifetime services. Job keys must be stable and non-empty or scheduling fails.

Test signals: constructor schedules rescans, max-job enforcement, table allocation failure, list output under lock, cancel-by-key and cancel-all, and shutdown/destructor behavior in controlled tests.
