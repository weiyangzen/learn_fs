# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcBackup.cc

Purpose: implements background dataset backup orchestration: discover datasets needing backup, stage them into an arena, reserve tape-buffer space, run preparation/archive/post scripts, and mark metadata complete.

Important APIs/types/functions: `XrdOssArcBackupTask::{BkpXeq,~XrdOssArcBackupTask}`, `XrdOssArcBackup::BkpWorker::DoIt`, constructor, `Add2Bkp`, `Archive`, `DoIt`, `GetManifest`, and `StartWorkers`. Static queue state includes `dsBkpQ`, `dsBkpQMtx`, `dsBkpQCV`, `numRunning`, and `maxRunning`.

Control flow: each scope job periodically calls `GetManifest()`, which runs `BkpUtilProg list` and enqueues new dataset names until `%%%`. Worker jobs pop tasks forever. A task creates a dataset arena, runs `bkputils setup` to get file/byte counts and manifest, optionally waits for `fsMon.Permit`, optionally runs `preparc`, runs the archive utility, optionally runs `postarc`, then runs `bkputils finish` to update metadata. `Archive()` builds a local or remote tape path and executes the archiver script.

State and persistence behavior: persistent effects are extensive: creates staging directories under `dsetRepoPFN`, writes manifests, creates/moves zip archives under the tape buffer or remote target, optionally deletes staging, and updates Rucio-like metadata keys. Runtime state tracks queued datasets, per-scope duplicate suppression sets, reserved bytes in `fsMon`, and scheduler jobs.

Dependencies: `XrdScheduler`, underlying `XrdOss`, `XrdOssArcConfig`, `XrdOssArcCompose`, `XrdOssArcFSMon`, `XrdOssArcStopMon`, `XrdOucProg`, `XrdOucStream`, `XrdOucUtils`, and XrdSys mutex/condition primitives.

Integration points: started by `XrdOssArcConfig::Configure`. It relies on external utilities (`XrdOssArc_BkpUtils`, archiver, optional pre/post tools) as the actual metadata and archive engines.

Risks: workers loop forever and are never deleted; failed tasks are deleted and rely on later manifest polls for retry; `numRunning` is decremented when idle and may not reflect live worker objects clearly; duplicate set owns `char*` pointers shared with tasks; external script output format is strict; local-space waits depend on semaphore redrive from `fsMon.Release`.

Test signals: manifest EOF handling, duplicate suppression, setup output parsing, local/remote archive path formation, pre/post script failures, finish failure, insufficient-space wait/release, stop-file pause behavior, and retry on next poll after failure.
