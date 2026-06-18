# sources/distributed-fs/xrootd/src/XrdOss/XrdOssStage.cc

Purpose: implements OSS staging from remote/mass storage to local disk. It supports queued staging through an external staging message program or FRC proxy, and real-time staging through internal priority queues and worker threads.

Important APIs/types/functions: `XrdOssSys::Stage`, `Stage_QT`, `Stage_RT`, `Stage_In`, `CalcTime`, `GetFile`, `getID`, `HasFile`, callback predicates `XrdOssFind_Prty` and `XrdOssFind_Req`, and the no-op scrub callback `XrdOssScrubScan`.

Control flow: `Stage()` dispatches to real-time or queued mode. Queued mode first checks `.fail` hold files, scrubs a path table, suppresses duplicate requests, optionally sends to `StageFrm`, otherwise formats a default or substituted stage message and feeds `StageProg`. Real-time mode rejects missing commands, deduplicates against `StageQ.fullList`, retries or holds failures, translates local/remote paths, stats remote size unless `XRDEXP_NOCHECK`, inserts a request into `fullList` and priority-ordered `pendList`, posts a semaphore, and returns an ETA. `Stage_In()` workers wait on `ReadyRequest`, pop pending requests, mark active, run `GetFile()` without holding the lock, update moving averages, delete successful requests, or mark failures with a hold timeout.

State and persistence behavior: global static queues, mutexes, semaphores, path hash tables, moving counters (`pndbytes`, `stgbytes`, `totbytes`, `totreqs`, `badreqs`), speed estimates, and failure hold timestamps drive runtime behavior. Persistent side effects are external: staged files appear on local storage, `.fail` files suppress retry loops, and external programs/scripts perform transfers.

Dependencies: `XrdOssApi`, `XrdOssOpaque`, `XrdOucEnv`, `XrdOucProg`, `XrdOucMsubs`, `XrdOucReqID`, `XrdFrcProxy`, local/remote name-to-name mappers, mass-storage `MSS_Stat`, and global `OssEroute`.

Integration points: called by OSS open/prepare paths when a file is remote. It bridges XRootD requests, FRC queues, external staging scripts, path translation, priority CGI variables, and cache accounting by delivering local files for later OSS operations.

Risks: queue state is shared across threads and lock scope is delicate; `req.path` is allocated before some early returns; external command output/return codes define correctness; `.fail` timestamps can suppress valid retries; ETA uses moving averages and can be inaccurate; real-time duplicate detection depends on hash plus string compare.

Test signals: queued duplicate suppression, `.fail` hold expiry, FRC and `StageProg` failures, priority ordering, worker success/failure state transitions, `XRDEXP_NOCHECK`, remote stat failures, and concurrency stress with multiple stage threads.
