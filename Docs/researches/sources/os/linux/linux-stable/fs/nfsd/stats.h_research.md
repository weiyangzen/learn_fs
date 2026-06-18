# File Research: sources/os/linux/linux-stable/fs/nfsd/stats.h

## Summary
Inline helpers and declarations for NFSD statistics accounting.

## Contents
Declares proc stats init/shutdown and wraps per-net `percpu_counter` updates for reply cache hits, misses, nocache, stale filehandles, read/write bytes, payload misses, duplicate-reply-cache memory usage, and NFSv4 write-delegation GETATTR.

## Important Details
Filehandle stale and IO byte helpers update both namespace-wide counters and per-export counters when an export stats object is present.

## Risks
Callers must pass the correct `nfsd_net` and optional `svc_export` so global and per-export accounting remain aligned. These helpers are intentionally lightweight and do not perform lifetime validation on the export stats pointer beyond null checks.
