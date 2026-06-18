# sources/distributed-fs/xrootd/src/XrdOss/XrdOssStat.cc

Purpose: implements OSS stat and space-query operations for files, physical files, logical space, extended attributes, export attributes, and XML-like OSS statistics.

Important APIs/types/functions: `XrdOssSys::Stat`, `StatFS` overloads, `StatLS`, `StatPF`, `StatVS`, `StatXA`, `StatXP`, `getCname`, and `getStats`.

Control flow: `Stat()` translates LFN to local PFN when configured, invokes a stat plug-in or `stat`, masks write bits for read-only exports, optionally updates atime, and falls back to remote MSS stat when local ENOENT can mean offline data. `StatFS()` derives export flags from `PathOpts`, asks `XrdOssCache_FS` for free/total bytes, and formats protocol responses. `StatLS()` maps path/env to a cache group and formats CGI-style space data. `StatPF()` returns physical file stat or device/partition metadata. `StatVS()` optionally rescans cache state, returns aggregate or named-space totals, and can request partition vectors for `+space`. `StatXA()` emits logical attributes; `StatXP()` returns export option flags. `getStats()` formats path and space statistics for daemon monitoring.

State and persistence behavior: mostly read-only queries, except `Stat()` can mutate file atime with `utime()` and `StatVS(updt)` can trigger cache scans. Reported state comes from local files, remote MSS, cache group tables, quota/usage accounting, and path export options.

Dependencies: `XrdOssCache`, `XrdOssConfig`, `XrdOssOpaque`, `XrdOssPath`, `XrdOssSpace`, `XrdOucEnv`, `XrdOucName2Name`, `XrdOucPList`, stat plug-in hooks, and POSIX stat/utime.

Integration points: backs XRootD stat, query, filesystem, locate, and monitoring paths. It connects namespace translation, cache partition accounting, remote MSS presence, virtual-space API (`XrdOssVSInfo`), and optional stat plug-ins.

Risks: remote fallback relies on `errno` after plug-in/stat failures; formatted responses must fit caller buffers; atime updates are side effects in a stat path; cache stats can be stale without scans; `StatPF` intentionally bypasses the custom stat plug-in; `StatVS` partition vectors transfer ownership to callers.

Test signals: local hit/miss, remote offline hit, read-only bit masking, atime update, stat plug-in v1/v2 behavior, cache/no-cache `StatLS`, `+space` partition return, buffer truncation, and monitor stats sizing.
