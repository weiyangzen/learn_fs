# File Research: sources/virtualization/nbdkit/plugins/nfs/nfs.c

## Purpose
Implements the `nfs` plugin, exposing a file inside an NFS export as an NBD disk through libnfs.

## Main Entry Points
- `nfs_plugin_config()` accepts `uri=` and `readonly=`.
- `nfs_plugin_get_ready()` initializes libnfs, configures libnfs logging/debugging, parses the RFC 2224 NFS URI, mounts the NFS export, and opens the remote file for non-multithreaded libnfs builds.
- `nfs_plugin_after_fork()` starts libnfs multithreading support and opens the file when that optional feature exists.
- `open_file()` opens the NFS file read-only or read-write.
- `nfs_plugin_get_size()` uses `nfs_fstat64`.
- `nfs_plugin_pread()` and `nfs_plugin_pwrite()` loop until the full requested range is transferred.
- `nfs_plugin_flush()` calls `nfs_fsync`.

## Internal Mechanics
The libnfs context, parsed URL, and file handle are global to the plugin. Per-client handles only store whether the connection was opened readonly. If libnfs was built with `nfs_mt_service_thread_start`, the plugin declares `NBDKIT_THREAD_MODEL_PARALLEL`; otherwise it serializes all requests.

## Dependencies
Uses libnfs (`nfsc/libnfs.h`, raw RPC logging APIs), nbdkit plugin API v2, POSIX open flags, sysconf page-size helpers, and optional libnfs multithreading APIs.

## Risks and Notes
The plugin assumes a single global NFS file handle is safe under libnfs multithreading when available; otherwise it forces serialized requests. `nfs_plugin_pwrite()` checks `r < -1`, but libnfs errors are generally negative values, making exact `-1` handling subtle. `nfs_plugin_pread()` logs an error on negative read but does not immediately return before checking `r == 0` and then advancing by `r`, which relies on libnfs not returning negative values other than the handled path; this deserves care if libnfs return conventions change.
