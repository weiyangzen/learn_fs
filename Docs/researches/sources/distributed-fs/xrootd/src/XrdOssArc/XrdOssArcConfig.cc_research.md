# sources/distributed-fs/xrootd/src/XrdOssArc/XrdOssArcConfig.cc

Purpose: implements archive plug-in configuration, validation, helper-program setup, environment export, filesystem monitor initialization, and scheduling of backup scopes/workers.

Important APIs/types/functions: constructor defaults, `BuildPath`, `Configure`, `ConfigPath`, `ConfigProc`, `ConfigXeq`, `GenLocalPath`, `Usable`, directive parsers `xqArcsz`, `xqBkup`, `xqBkupPS`, `xqBkupScope`, `xqGrab`, `xqManf`, `xqPaths`, `xqRse`, `xqRucio`, `xqStage`, `xqTrace`, and `xqUtils`.

Control flow: defaults establish utility names, logical prefixes, admin/stop/tape/stage paths, metadata names, poll limits, backup mode, archive size policy, and tracing. `Configure()` gathers `ossarc.*` directives, exports debug/RSE/Rucio/checksum/size env vars, creates/validates admin and stop paths, initializes stop and free-space monitors, validates source data, builds the dataset backup arena, resolves and sets up helper programs, exports MSS settings, verifies metadata keys, constructs backup jobs for configured scopes, starts workers, and schedules initial scans. Directive parsing accepts `arcsize`, `backup`, `manifest`, `msscmd`, `paths`, `rsedcl`, `rucio`, `stage`, `trace`, and `utils`.

State and persistence behavior: stores configuration in heap-allocated C strings and program objects for daemon lifetime. It creates directories for admin and dataset backup arenas, initializes stop-file monitoring, exports environment variables consumed by external scripts, and schedules recurring jobs.

Dependencies: `XrdScheduler`, underlying `XrdOss`, backup/FS/stop monitors, `XrdOuca2x`, `XrdOucGatherConf`, `XrdOucProg`, `XrdOucUtils`, POSIX stat/access concepts, and global `ossP`, `schedP`, `Elog`, `ArcTrace`, `fsMon`, `ecMsg`.

Integration points: called from `XrdOssArc::InitArc`; it wires all external scripts (`BkpUtil`, `MssCom`, archiver, optional pre/post) and starts archive background processing.

Risks: manual string ownership and daemon-lifetime leaks; `Usable()` permission checks compare group write bit with `st_uid` instead of group id; unknown directives mostly warn but missing required RSE/scopes fail; external helper setup is startup-critical; no dynamic reconfiguration; path prefixes and tape paths are mutable global assumptions.

Test signals: parse every directive and invalid option, relative path rejection, RSE/scopes required, env exports, helper path qualification, local vs remote backup mode, archive-size range validation, metadata key failure warning, stop/admin/tape path validation, worker scheduling only when no fatal config errors.
