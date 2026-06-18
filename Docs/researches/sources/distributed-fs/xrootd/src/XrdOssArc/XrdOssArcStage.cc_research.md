# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcStage.cc

Purpose: implements asynchronous staging of archive files from a mass-storage-system buffer into the local online tier. It deduplicates concurrent staging requests for the same archive path and limits active staging jobs by `Config.maxStage`.

Important APIs/functions: `Stage(path, mssPath)` is the entry point used by archive opens. It checks the `Active` set, asks `isOnline(mssPath)` through `Config.MssComProg->Run("online", path)`, inserts a copied path into `Active`, schedules a `XrdOssArcStage` job when concurrency is available, or pushes a path into `Pending`. `DoIt()` opens the archive path to force staging, records errors with `StageError()`, drains queued paths, removes active entries through `Reset()`, then self-deletes. `isOnline()` maps `XrdOucProg` negative status conventions back to `MssRC`.

State/control: global `Active` stores `ActInfo` records keyed by path and error code; `Pending` queues path pointers owned by active records; `stageMtx` protects active state and `schedMtx` protects staging slots/queue. Persistence is in the MSS/cache state, not the process.

Dependencies/integration: uses `XrdScheduler`, `XrdOucProg`, `XrdSysFD_Open`, `Config.MssComName`, `Config.maxStage`, and tracing. Risks include pointer lifetime coupling between `Active` and `Pending`, lock ordering mistakes, `StageError()` checking an iterator after unlocking, and `Config.maxStage++` relying on `schedMtx` still being held after the loop break. Tests should simulate duplicate requests, stage failure propagation, queue draining, and online/offline/invalid MSS status.
