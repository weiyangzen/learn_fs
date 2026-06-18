# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/client/nfs_kdtrace.h

## Purpose
Declares DTrace/KDTRACE probe identifiers and probe-call macros for NFS client access-cache and attribute-cache events.

## Main Interfaces
- Declares access-cache probe IDs: flush done, get hit, get miss, and load done.
- Declares attribute-cache probe IDs: flush done, get hit, get miss, and load done.
- When `KDTRACE_HOOKS` is enabled, macros invoke function pointers from `<sys/dtrace_bsd.h>` only if the relevant probe is registered.
- When `KDTRACE_HOOKS` is disabled, all macros compile to no-ops.

## Integration
Used by `nfs_clvnops.c` and related cache code to instrument cache invalidation, lookup hits/misses, and cache reload completion without imposing runtime overhead when tracing is disabled.

## Risks
- Probe macros assume the DTrace hook declarations match the argument signatures exactly.
- Since the non-KDTRACE path is empty, tracing code must not rely on side effects inside macro arguments.
