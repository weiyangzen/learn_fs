## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmPurge.cc

Purpose: implements space-based purge policy. It scans namespaces, selects eligible resident files by access age and migration/pin state, optionally asks an external policy program, removes files through the OSS layer, notifies CMS/CNS, emits monitor records, and trims old empty directories.

Important APIs and control flow: `Policy()` creates per-space policy objects. `Init()` prunes policies without spaces, enables requested spaces, converts percent thresholds to byte thresholds, and starts `PolProg` when external policy is used. `Purge()` calls `LowOnSpace()`, reports `Stats()`, then rotates over enabled spaces calling `PurgeFile()` until each reaches `maxFSpace` or cannot proceed. `Scan()` walks configured paths using `XrdFrmFiles`, screens filesets, calls `Add()`, and may use `XrdFrmPurgeDir` callback to remove empty directories. `Eligible()` enforces hold time, fail files, migration copy-time, and pin flags. `PurgeFile(fset,pfn)` unlinks via `Config.ossFS`, converts PFN to LFN when possible, notifies `cmsPath`/`XrdFrmCns`, and maps purge monitor data.

State and persistence: per-policy state tracks free/used space, thresholds, counts, deferred queues, and an `XrdFrmTSort` of candidates. Persistent effects include deleted data, removed directories, CNS/CMS updates, and external fail/sidecar files observed by `XrdFrmFileset`.

Dependencies and integration: uses `XrdOssVSInfo` space stats, `XrdFrmFiles`, `XrdFrmTSort`, `XrdFrmCns`, `XrdFrmMonitor`, `XrdNetCmsNotify`, and optional `XrdOucProg` policy program.

Risks and test signals: destructive behavior depends on many gates; test mode must be verified for file and directory removal. `Advance()` appears to return no deferred item when `time(0) - DeferT[n] > Hold`, which is counterintuitive for an age threshold and deserves regression coverage. `nowT` static initialization in `Scan()` can stale time-dependent scheduling. Tests should cover pin variants, migrated/unmigrated old/new metadata, external policy responses `y/n/a`, CMS/CNS notifications, space threshold math, and directory mtime restoration.
