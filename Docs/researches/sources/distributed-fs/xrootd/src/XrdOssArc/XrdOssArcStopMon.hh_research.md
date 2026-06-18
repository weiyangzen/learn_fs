# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcStopMon.hh

Purpose: declares the stop monitor/job used to pause archive activity without abruptly killing workers. It supports a long-lived parent scheduler job and short-lived child guards around operations.

Important APIs/types: `DoIt()` is parent-only. `Activate()` and `Deactivate()` manage a shared lock, guarded by `RAtomic_bool isActive` to avoid duplicate lock/unlock. The parent constructor takes admin path, check interval, and success output flag. The child constructor takes a parent pointer, aliases its `xsLock`, marks itself active, and immediately locks shared. Copy/assignment are deleted.

Control/state behavior: parent owns an open admin directory and scheduled polling; children own only shared lock participation. The exclusive parent lock is acquired only in the implementation when STOP appears. Persistence is file-based via STOP/IDLE, while lock state is in process memory.

Dependencies/integration: depends on `XrdJob`, `XrdSysRAtomic`, and `XrdSysXSLock`; `XrdOssArcFile::Open()` uses child instances to wrap restore/stage decisions. Risks include parent lifetime assumptions, manual activation discipline if child instances are reused, and process abort on invalid parent destruction. Test signals: RAII child construction/destruction, repeated `Activate`/`Deactivate`, and lock contention with simulated STOP.
