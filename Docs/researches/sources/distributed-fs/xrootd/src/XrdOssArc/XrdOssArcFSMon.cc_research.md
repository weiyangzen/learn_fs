# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcFSMon.cc

Purpose: monitors tape-buffer filesystem capacity and gates local backup tasks so the archive process preserves configured free space.

Important APIs/types/functions: `XrdOssArcFSMon::Init`, `DoIt`, `Permit`, `Release`, and private `getFSpace`. Platform macros map `statfs` fields across Linux/BSD/macOS.

Control flow: `Init()` reads filesystem size/free bytes, computes minimum free space from either percentage (negative config value) or bytes, logs startup capacity, stores path/update interval, and schedules periodic updates. `DoIt()` refreshes size/free/used counters under lock and reschedules itself. `Permit()` reserves bytes for a backup if `fs_inUse + fs_inBkp + taskBytes <= fs_MaxUsed`; otherwise it queues the task and tells caller to wait. `Release()` drops reserved bytes, refreshes filesystem stats, posts semaphores for queued tasks that now fit, and logs remaining blocked backups.

State and persistence behavior: runtime memory state tracks filesystem size, free, minimum free, maximum used, bytes already committed to backups, update interval, path, mutex, and waiting task queue. It does not persist data, but controls when backup tasks create large archive files.

Dependencies: platform `statfs`, `XrdScheduler`, `XrdOssArcBackupTask`, `XrdOucUtils::HSize`, `XrdSysError`, and trace globals.

Integration points: initialized by config and used by backup tasks in local backup mode. It is the resource lease manager for tape-buffer disk space.

Risks: queued tasks are raw pointers owned by backup workers; if a task is destroyed while queued, the wait queue would dangle. `Release()` posts waiters but only increments local `nTot`, not `fs_inBkp`, until waiters rerun `Permit()`, so races depend on mutex/semaphore sequencing. `size_t` arithmetic can overflow on very large filesystems or task sizes.

Test signals: percentage and absolute minfree calculations, startup below-minfree warning, permit success/failure, release waking multiple tasks in order, periodic refresh, statfs failure logging, and concurrent permit/release stress.
