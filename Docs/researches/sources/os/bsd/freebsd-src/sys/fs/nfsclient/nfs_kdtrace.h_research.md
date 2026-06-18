# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_kdtrace.h

## Purpose
Declares FreeBSD DTrace/KDTRACE probe IDs and probe-call macros for NFS client access-cache and attribute-cache events.

## Main Interfaces
- Declares access-cache probe IDs for flush done, get hit, get miss, and load done.
- Declares attribute-cache probe IDs for flush done, get hit, get miss, and load done.
- When `KDTRACE_HOOKS` is enabled, macros call hook function pointers from `<sys/dtrace_bsd.h>` only when the corresponding probe is registered.
- When `KDTRACE_HOOKS` is disabled, all macros compile to no-ops.

## Integration
Used by `nfs_clvnops.c` and related client cache code to instrument access-cache hits/misses/loads and attribute-cache invalidation/hits/misses/loads without adding runtime side effects when tracing is disabled.

## Risks
- Probe macro argument expressions must not be required for side effects, because the disabled path expands to nothing.
- The enabled path depends on the DTrace hook function pointer signatures matching the macro arguments exactly.
