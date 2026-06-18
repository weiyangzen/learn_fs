# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_log.c

## Purpose

`nfs_log.c` implements kernel-side NFS server logging buffer management and log record emission. It creates per-log-buffer in-progress files, queues XDR-encoded NFS log records, flushes records to disk, rotates buffers for user-level log processing, and provides synthetic logging records for share, unshare, public filehandle lookup, and `getfh`.

The XDR field-level encoders are in `nfs_log_xdr.c`; this file owns allocation, dispatch selection, buffering, file I/O, and integration with export and request dispatch code.

## Main Data Structures

`struct lr_alloc` is a private header placed before each allocated record buffer. It tracks circular-list links, allocation flags, encoded record address and size, owning kmem cache, related export, and held `log_buffer`.

`struct log_buffer` instances are shared by exports using the same `ex_log_buffer` path. Each buffer tracks a reference count, path, active `log_file`, queued records, number of queued records, queued byte count, and lock. All buffers are linked on global `nfslog_buffer_list`, protected by `nfslog_buffer_list_lock`.

`struct log_file` represents the currently open in-progress file for a buffer. It tracks path, vnode, refcount, writer count, error/printed/waiting flags, and lock/condition variable coordination.

Three kmem caches back record buffers: small, medium, and large. `nfslog_write_record()` retries with larger caches if XDR encoding does not fit.

## Initialization and Export Setup

`nfslog_init()` initializes the global buffer-list rwlock and creates the small/medium/large record allocation caches. It is called from export initialization.

`nfslog_setup()` attaches logging to an export. It first searches `nfslog_buffer_list` for an existing `log_buffer` whose path matches the export's `ex_log_buffer`. If found, it holds that buffer and attaches it to `exi->exi_logbuffer`. Otherwise it creates a new buffer and backing log file, then reacquires the writer lock and searches again to avoid duplicate creation races. New buffers are inserted into the global list and held once for the list and once for the export.

`nfslog_disable()` releases an export's buffer. Final release flushes queued records, removes the buffer from the global list if no new user raced in, releases the backing file, frees the path, and frees the buffer.

## Log File Lifecycle

`log_file_create()` opens `original_path + LOG_INPROG_STRING` using `vn_open()` with create/write flags. It allocates `struct log_file`, stores the vnode reference returned by `vn_open()`, and writes an NFS log buffer header when the file is empty. The header is built by `create_buffer_header()` with `NFSLOG_BUF_VERSION`, timestamp, flags, offset, and a final size patched into the first XDR word.

`log_file_rele()` closes and releases the vnode when the refcount reaches zero, destroys state, and frees the path and structure.

`nfslog_logbuffer_rename()` is the log-rotation path used by `nfsl_flush()`. It flushes queued records, holds the current `log_file`, renames the in-progress file to the daemon-visible buffer path, creates a fresh in-progress file, swaps it into the `log_buffer`, releases the old buffer reference, and waits for old writers to drain before returning.

## Record Allocation, Queueing, and Flush

`nfslog_record_alloc()` allocates a record buffer from a selected kmem cache and returns the payload area after the `lr_alloc` header. If the export still has `EX_LOG`, it holds the export's `log_buffer` and stores it in the record header. The caller receives the `lr_alloc` as an opaque cookie.

`nfslog_record_put()` either discards invalid/empty records, appends public-filehandle records to every buffer, or enqueues the record on its buffer's circular list. It flushes immediately when queued bytes exceed `nfslog_num_bytes_to_write`, record count exceeds `nfslog_num_records_to_write`, or the caller requests sync.

`nfslog_records_flush_to_disk()` and `_nolock()` detach the current queued circular list while holding `lb_lock`, reset queue counters, hold the current `log_file` as a writer, write all records, release writer state, then free the record list.

`nfslog_write_logrecords()` builds an iovec array over encoded records and appends them to the log vnode with `VOP_WRITE()`. It takes a vnode write lock, snapshots file size, enforces a 32-bit maximum buffer file size, and rolls the file size back with `VOP_SETATTR()` if the write fails after size growth. It suppresses repeated warning messages using `L_PRINTED` and reports re-enable when errors clear.

`nfslog_free_logrecords()` frees a circular list of `lr_alloc` records. For normal records it releases the held log buffer and returns the allocation to its cache. `LR_ALLOC_NOFREE` lets one encoded record be reused across all buffers during public-filehandle logging.

## Flush System Call

`nfsl_flush()` copies a `nfsl_flush_args` request from userspace. It validates version, optionally copies a specific buffer name, and either performs the flush synchronously or starts a zthread for asynchronous work.

`nfslog_do_flush()` scans the buffer list with per-buffer holds. `NFSL_ALL` flushes queued records for each live buffer. A specific `NFSL_RENAME` request rotates the matching live buffer. If the requested buffer is not live, it still attempts to rename `buffer + LOG_INPROG_STRING` to `buffer`, which lets the daemon process inactive in-progress files.

There are some early-return paths in `nfsl_flush()` after allocating `tparams` or `buff` that return without freeing previously allocated memory; these are worth preserving as audit notes if this legacy code is ever touched.

## Logging Dispatch Tables

The file defines logging dispatch tables separate from normal NFS dispatch:

- NFSv2 procedures map to logging XDR routines for handles, args, minimal results, and transaction-affecting flags.
- NFSv3 procedures map similarly, with `READDIRPLUS` using a medium record allocation.
- Synthetic `NFSLOG_PROGRAM` version 1 procedures cover share, unshare, lookup, and getfh records.

Each `nfslog_proc_disp` stores argument encoder, result encoder, and whether the operation affects transaction processing. `nfslog_write_record()` skips non-transaction-affecting operations unless the export has `EX_LOG_ALLOPS`.

## Request Logging Flow

`nfslog_get_exi()` determines which export should receive a log record and allocates a record ID. Normally it returns the request's export when that export has `EX_LOG`. It also handles the WebNFS/public-filehandle edge case where a multicomponent lookup starts through the non-logged public export but returns a filehandle in a logged export; in that case it inspects successful v2/v3 lookup results and finds the returned export by filehandle.

`nfslog_write_record()` selects the logging dispatch entry by RPC program/version/procedure, chooses an initial allocation size, XDR-encodes the record header plus operation args/results, retries in larger record buffers when encoding fails, patches the final encoded length into the record's first XDR word, then queues or synchronously writes the record. Share/unshare records use record ID 0 and are written synchronously.

Public-filehandle state changes call `log_public_record()`, which fabricates an `NFSLOG_LOOKUP` record and appends it to all open buffers. `nfslog_share_record()` logs a synthetic share record to the export's buffer when applicable and always emits the public record when any buffer exists. `nfslog_unshare_record()` emits the synthetic unshare record. `nfslog_getfh()` records privileged getfh operations with filehandle and path.

## Dependencies and Integration Points

- Export state from `exportinfo_t`, including `EX_LOG`, `EX_LOG_ALLOPS`, log buffer path, tag, public export, and filehandle templates.
- Filehandle lookup helpers from `nfs_export.c`: `checkexport()`.
- XDR encoders from `nfs_log_xdr.c`.
- VFS/vnode file I/O: `vn_open()`, `vn_rename()`, `VOP_GETATTR()`, `VOP_WRITE()`, `VOP_SETATTR()`, `VOP_CLOSE()`, vnode locking.
- RPC request metadata: `svc_req`, transport remote address, credential flavor, netid.
- Kernel threading for asynchronous flush via `zthread_create()` and `zthread_exit()`.
- Atomic record ID allocation via `atomic_add_32_nv()`.

## Concurrency and Locking Notes

`nfslog_buffer_list_lock` protects global list traversal and insertion/removal. Buffer refcounts are protected by `lb_lock`; file refcounts and writer counts by `lf_lock`. Record queue manipulation occurs under `lb_lock`. Actual file writes are serialized through `LOG_FILE_LOCK_TO_WRITE()` and vnode write locking.

The rename path carefully swaps `lb_logfile` under `lb_lock` so new writers see the new file, then waits for old `lf_writers` to drain before returning the renamed file to user-level processing.

## Risks and Edge Cases

- `nfsl_flush()` has error paths after allocations that do not free `tparams` or copied buffer storage.
- The log file size cap is `MAXOFF32_T`; once exceeded, logging stops for that buffer until state changes.
- `nfslog_write_record()` indexes dispatch tables by version/procedure after selecting a program; it assumes normal server dispatch has already validated requests.
- Public-filehandle logging reuses one record for every buffer by toggling `LR_ALLOC_NOFREE`; mistakes in circular-list relinking would corrupt subsequent writes.
- Logging records intentionally omit file data and encode compact summaries; consumers must not treat them as full RPC replays.
- Buffer removal races are handled by an extra temporary ref in `log_buffer_rele()`, but future changes must preserve that pattern.

## Testing and Verification Signals

Useful tests cover concurrent exports sharing a log buffer, share/unshare logging, public-filehandle lookup into logged exports, synchronous and asynchronous `nfsl_flush()`, buffer rename while writes are active, queue threshold flushing, ENOSPC/write-error recovery, oversized record retry from small to medium/large buffers, and cleanup when the last export using a buffer is unshared.
