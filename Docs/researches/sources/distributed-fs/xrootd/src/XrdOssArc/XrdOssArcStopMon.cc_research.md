# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcStopMon.cc

Purpose: implements administrative stop/drain behavior for archive backup and restore work. A parent monitor watches an admin directory for a `STOP` file; child instances acquire shared locks around active operations so the parent can wait for drain and create an `IDLE` marker.

Important APIs/functions: the parent constructor opens the admin path as a directory, removes stale `IDLE`, and schedules periodic `DoIt()`. The child constructor shares the parent's `XrdSysXSLock` and locks it shared. `DoIt()` checks `STOP` with `fstatat`, takes the exclusive lock, creates `IDLE`, sleeps until `STOP` disappears, removes `IDLE`, releases the lock, and reschedules. The destructor aborts if a fully constructed parent is deleted; child destruction calls `Deactivate()`.

State/control: `admDirFD >= 0` marks the parent. The lock serializes global stop state versus per-operation shared activity. Persistence is filesystem-signaled through `STOP` and `IDLE` files in `admPath`.

Dependencies/integration: uses `XrdScheduler`, `XrdSysXSLock`, `XrdSysFD_Open`, `XrdSysTimer`, POSIX `openat/unlinkat/fstatat`, and `Elog`. Risks include indefinite sleep while STOP remains, abort-on-parent-delete behavior, constructor failure cleanup, and dependency on admin directory lifetime. Tests should cover STOP detection, IDLE creation/removal, child lock blocking, parent deletion guard, and permission errors.
