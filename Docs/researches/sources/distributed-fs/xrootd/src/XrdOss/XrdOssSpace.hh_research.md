# sources/distributed-fs/xrootd/src/XrdOss/XrdOssSpace.hh

Purpose: declares `XrdOssSpace`, the static accounting interface used by the OSS cache layer to track per-space usage and quotas. The class models named spaces and byte totals for service, prestage, purge, admin, reserved, and additive categories.

Important APIs/types/functions: `sType`, `uEnt`, `Adjust(int/off_t/sType)`, `Adjust(const char*/off_t/sType)`, `Init()`, `Init(aPath,qFile,isSOL,us)`, `Quotas()`, `Unassign()`, and `Usage()` by group id or group name. Private helpers `Assign`, `findEnt`, `Readjust`, and `UsageLock` implement table management and synchronized usage-file access.

Control flow: the header exposes only contracts. Callers initialize the shared accounting files, assign or find a named entry, adjust byte counters as files are added/removed, and query totals. The `haveUsage` and `haveQuota` flags tell callers which backing features are active.

State and persistence behavior: state is static and process-global. `uData` and `uDvec` form an in-memory table capped by `DataSz/sizeof(uEnt)`, while `qFname`, `uFname`, `uUname`, file descriptor `aFD`, mtimes, free/fence cursors, and sync/adjust flags indicate persistent usage/quota files. `Solitary` controls whether one process owns the files.

Dependencies: forward-declares `XrdSysError`; implementation integrates with `XrdOssCache` via friendship and with filesystem locking and quota files elsewhere in XrdOss.

Integration points: `XrdOssCache` uses this class for cache-group usage accounting, quota decisions, and stat reports such as `StatLS`/`StatVS`.

Risks: fixed-size tables can overflow for many cache groups; stale file mtimes or failed locks can desynchronize counters; all state is static, so tests and multiple OSS instances need isolation. Byte adjustments must be paired with unlink/create paths or usage drifts.

Test signals: initialize with and without quota files, verify named/group-id `Usage`, exercise concurrent `Adjust`, overflow group count, stale usage-file reload, and quota-disabled behavior.
