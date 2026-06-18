<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/svc_run.c -->
# sources/user-network-fs/nfs-utils/utils/mountd/svc_run.c

## Purpose

`svc_run.c` provides `rpc.mountd`'s custom RPC event loop, extending the usual `svc_run` behavior to process kernel export-cache file descriptors as well as RPC transports.

## Important APIs, types, and functions

Public function `my_svc_run` loops forever. On some 64-bit glibc builds, private `my_svc_getreqset` replaces buggy old `svc_getreqset` behavior by iterating fd masks and calling `svc_getreq_common`.

## Control flow

Each loop copies `svc_fdset`, passes it to `cache_process`, and, if selected RPC descriptors remain, dispatches them through `svc_getreqset`. A negative select/cache result logs an error and returns to the caller.

## State and persistence behavior

The loop operates on global SunRPC `svc_fdset` and kernel export cache descriptors managed elsewhere. It does not persist data directly.

## Dependencies and integration points

It depends on tirpc/SunRPC globals, `cache_process` from export support code, and `xlog`. `mountd.c` calls `my_svc_run` after listener and cache-worker initialization.

## Risks and edge cases

The loop exits on select errors, which causes `mountd.c` to log unexpected termination and exit. FD set size is capped at `FD_SETSIZE` in the compatibility path. Any cache processing bug can starve RPC dispatch or terminate the daemon.

## Test signals

Tests should exercise cache-only activity, RPC-only activity, mixed readiness, select error handling, high fd values near `FD_SETSIZE`, and the glibc compatibility path where available.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/svc_run.c -->
