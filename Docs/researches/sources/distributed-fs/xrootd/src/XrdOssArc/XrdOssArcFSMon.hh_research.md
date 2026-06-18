# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcFSMon.hh

Purpose: declares `XrdOssArcFSMon`, the filesystem-space admission controller used by archive backup workers. It is an `XrdJob` scheduled periodically to refresh filesystem size/free counters and to release blocked backup tasks when enough space is available.

Important APIs/types: `Init(path, fVal, fsupdt)` initializes path, free-space policy, and refresh cadence; `Permit(XrdOssArcBackupTask*)` reserves bytes for a backup or queues the task; `Release(size_t)` releases reserved bytes and posts waiting task semaphores; `DoIt()` is the scheduled refresh hook; `getFSpace()` is the platform statfs wrapper. State is guarded by `rmMutex` and includes `btWaitQ`, `fs_inBkp`, `fs_inUse`, `fs_MaxUsed`, `fs_MinFree`, `fs_Free`, and `fs_Size`.

Control/state behavior: the monitor computes `fs_MaxUsed = fs_Size - fs_MinFree`, treats in-flight backups as committed bytes, and drives waiters in FIFO order after releases. Persistence is external: only live process memory is tracked; filesystem facts come from `statfs`.

Dependencies/integration: depends on `XrdJob`, `XrdSysMutex`, scheduler globals, and `XrdOssArcBackupTask` fields such as `numBytes`, `relSpace`, and `btSem`. Risks are stale accounting between refresh intervals, queued tasks that depend on correct `Release()` calls, and platform `statfs` differences. Test signals should include percentage and absolute free-space policy, queue wake-up ordering, failed statfs handling, and concurrent permit/release paths.
