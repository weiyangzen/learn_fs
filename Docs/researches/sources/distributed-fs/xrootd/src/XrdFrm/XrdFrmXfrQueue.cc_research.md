## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmXfrQueue.cc

Purpose: implements the in-memory transfer job queues, duplicate suppression table, notification delivery, free-job pool, stop-file monitoring, and fair queue selection used by transfer workers.

Important APIs and control flow: `Init()` creates per-queue stop-file names, starts one `StopMon()` thread per queue, and preallocates `2 * Config.xfrMax` free jobs for each queue. `Add()` validates queue number, suppresses duplicate active/pending work by request key, translates LFN to PFN, checks inbound/outbound existence preconditions, allocates a job, stores it in `hTab`, appends to the queue, and posts `qReady`. `Get()` waits for a job acceptable to the worker's IO type and calls `Pull()`. `Pull()` alternates between inbound and outbound queue pairs, skips stopped queues, chooses older add time, and dequeues. `Done()` sends notifications, deletes the persistent request, removes the active hash entry, and returns the job to the free pool.

State and persistence: in-memory state is protected by `hMutex` and `qMutex`. Persistent request files are deleted through `reqFQ`; notification side effects write to file or UDP destinations. Stop files under `Config.AdminPath` suspend queues until removed.

Dependencies and integration: used by `XrdFrmReqBoss`, `XrdFrmMigrate`, and transfer workers. Depends on `XrdFrcReqFile`, `XrdFrcRequest`, `XrdNetMsg`, `XrdOss`, and global `Config`.

Risks and test signals: notification parsing mutates `Notify` by replacing carriage returns with NULs, so copied request data must be isolated. `Pull()` indexes `xfrQ[theQ]` even when both queues are nil unless guarded by surrounding state; stopped-empty cases need tests. Tests should cover duplicate notification aggregation, stop-file suspend/resume, worker lane selection, free-pool exhaustion blocking, inbound/outbound existence rules, and unsupported notification paths.
