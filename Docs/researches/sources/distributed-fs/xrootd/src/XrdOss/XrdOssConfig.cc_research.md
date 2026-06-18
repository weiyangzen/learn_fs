# sources/distributed-fs/xrootd/src/XrdOss/XrdOssConfig.cc

## Purpose
Implements OSS subsystem initialization and parsing of `oss.*` configuration directives. It sets process limits, export/path flags, cache spaces, usage/quota files, staging/RSS commands, name-to-name and stat plugins, mmap policy, preread policy, transfer policy, and final display/stat-reporting state.

## Important APIs, types, and functions
`XrdOssSys::XrdOssSys()` initializes defaults for staging, cache scanning, FD fences, allocation, transfer, preread, stat plugin, and PFC mode. `Configure()` is the orchestration entry point: it registers OSS error tables, raises FD limits, maps devices, parses config with `ConfigProc()`, loads N2N/stat plugins, initializes cache/usage, configures staging, AIO, mmap, PFC, space reporting, prefix generation, stats, and the cache-scan thread. `ConfigXeq()` dispatches directives to handlers such as `xalloc`, `xspace`, `xpath`, `xstg`, `xstl`, `xusage`, and `xxfr`. `ConfigStage()` and `ConfigStageC()` validate remote storage/stage command requirements and start real-time stage threads or queue-style programs. `ConfigCache()`, `ConfigMio()`, `ConfigSpace()`, `ConfigStats()`, and `Config_Display()` resolve derived state.

## Control flow
Parsing is two-stage. `ConfigProc()` reads only `oss.*` and `all.export`, recording requested settings. `Configure()` then performs dependent passes in order: plugin loading, usage/quota init, staging/RSS setup, mmap/PFC flag reconciliation, export-list defaults, final space/stat setup, background scan startup, and final display. `xspace()` either builds one space, expands a wildcard directory into multiple spaces, or records assign/default mappings in `SPList`.

## State and persistence
This file mutates many `XrdOssSys` members and global integration points: `XrdOssRPList`, `OssTrace.What`, `RSSProg`, `StageProg`, `StageFrm`, `STT_Func/Fund`, `RPList`, `SPList`, `DPList`, cache group counts, and usage/quota paths. Persistence is configured by `oss.usage log` and `oss.usage quotafile`, which are passed to `XrdOssCache::Init()`/`XrdOssSpace`. Staging state can persist externally through queue programs or FRM admin paths.

## Dependencies and integration points
Heavy integration with `XrdOucStream`, `XrdOucExport`, `XrdOuca2x`, `XrdOucN2NLoader`, `XrdOucPinLoader`, `XrdOucProg`, `XrdFrcProxy`, `XrdOssCache`, `XrdOssMio`, `XrdOssSpace`, and the OSS API/export flag model. Environment variables such as `XRDDEBUG`, `XRDREDIRECT`, `XRDOSSCSCAN`, `XRDADMINPATH`, `XRDOFSEVENTS`, and `oss.runmode` alter behavior.

## Risks and test signals
This file is a high-blast-radius config hub. Risk areas include directive ordering, deprecated compatibility (`oss.cache`, `msscmd`), path wildcard expansion, mount verification return semantics, FD-limit platform quirks, PFC flag rewrites, plugin ABI selection, stage/RSS requirements, and error-text table length mismatch. Tests should use config fixtures that cover all directive handlers, invalid values, manager/solitary/PFC modes, macOS FD handling, and no-config defaults.
