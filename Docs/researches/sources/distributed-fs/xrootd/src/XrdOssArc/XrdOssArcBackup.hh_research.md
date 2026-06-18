# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcBackup.hh

Purpose: declares the backup scheduler job, backup task, worker job, and queue/set state used by the archive plug-in.

Important APIs/types/functions: `XrdOssArcBackupTask` fields `Owner`, `theScope`, `theDSN`, `numBytes`, `numFiles`, `relSpace`, and `btSem`; task method `BkpXeq`; `XrdOssArcBackup` methods `Archive`, `Arena`, `DoIt`, `StartWorkers`, `theScope`, constructor, private `Add2Bkp` and `GetManifest`; nested `BkpWorker`; comparator `cmp_str`.

Control flow: class inheritance from `XrdJob` lets both per-scope backup scans and worker loops run on `XrdScheduler`. Tasks wait on their own semaphore when filesystem space is unavailable.

State and persistence behavior: header declares process-global queue state shared by all scopes plus per-scope duplicate sets and arena path. Persistent effects are in implementation through external tools and filesystem staging.

Dependencies: STL `deque`, `set`, `string`, `XrdJob`, and `XrdSysPthread`.

Integration points: used by config to schedule backups and by `XrdOssArcFSMon` to wake waiting tasks.

Risks: static queue state spans all archive scopes; `char*` ownership is manual; comparator assumes non-null C strings; jobs are intentionally never deleted; the destructor does not free `myArena`.

Test signals: construction creates arena, `StartWorkers` schedules expected jobs, duplicate set erase on task destruction, semaphore wake from FS monitor, and multi-scope queue fairness.
