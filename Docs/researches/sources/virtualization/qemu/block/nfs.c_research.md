# File Research: sources/virtualization/qemu/block/nfs.c

## Purpose
Implements QEMU’s native NFS block driver backed by libnfs. It opens a file inside an NFS export, integrates libnfs asynchronous I/O with QEMU’s AioContext, and exposes block read/write/flush/truncate/create/stat behavior.

## Main Entry Points
- `nfs_parse_filename()` and `nfs_parse_uri()` convert `nfs://host/path?...` URLs into QDict/QAPI options.
- `nfs_file_open()` opens the NFS file and sets total sectors and zero-init support.
- `nfs_client_open()` initializes libnfs, applies UID/GID/TCP/readahead/pagecache/debug options, mounts the export, opens or creates the file, and records size/stat metadata.
- `nfs_co_preadv()`, `nfs_co_pwritev()`, and `nfs_co_flush()` issue libnfs async operations and yield the current coroutine until callbacks schedule it again.
- `nfs_file_co_create()` and `nfs_file_co_create_opts()` create and size NFS-backed images.
- `nfs_file_co_truncate()`, `nfs_co_get_allocated_file_size()`, `nfs_reopen_prepare()`, `nfs_refresh_filename()`, `nfs_dirname()`, and `nfs_refresh_limits()` implement metadata and block driver support.
- `nfs_attach_aio_context()` and `nfs_detach_aio_context()` move libnfs fd handlers between AioContexts.

## Internal Mechanics
`NFSClient` stores the libnfs context, open file handle, currently registered poll events, AioContext, mutex, cached stat data, server/path, and runtime tuning values. `nfs_set_events()` translates libnfs requested events into QEMU `aio_set_fd_handler()` read/write callbacks. Those callbacks call `nfs_service()` under the client mutex and refresh event registration.

Each coroutine request creates an `NFSRPC` task containing the sleeping coroutine and optional stat/iovec storage. Libnfs callbacks store the result, copy data for older libnfs APIs when needed, report errors, and use `aio_co_schedule()` rather than direct wakeup so the coroutine does not re-enter while the mutex is still held.

Reads may allocate a bounce buffer for multi-iovec requests on libnfs API v2 and zero-pad short reads. Writes allocate/copy a contiguous buffer when libnfs cannot consume the provided iovec directly and require the full byte count to succeed.

## Dependencies
Uses libnfs, QEMU block driver APIs, AioContext fd handlers, coroutine scheduling, QAPI block-core visitors, QDict option conversion, GLib URI parsing, QemuOpts create options, trace/error-report helpers, and optional libnfs feature macros for readahead, pagecache, debug, unmount, and Windows differences.

## Risks and Notes
The file is built around libnfs async callbacks plus a mutex; the callback intentionally schedules rather than directly wakes coroutines to avoid deadlock on immediate follow-up requests. Reopen does not reconnect to the NFS server; it only validates mode/cache constraints and refreshes stat data for read-only reopen. Readahead/pagecache options are rejected with `cache.direct=on` and prevent later reopening with `BDRV_O_NOCACHE`. `nfs_dirname()` refuses to synthesize a base directory when UID/GID query parameters are needed, because dropping those parameters would change semantics.
