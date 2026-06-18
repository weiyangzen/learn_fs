# File Research: sources/virtualization/qemu/block/iscsi.c

## Role

`block/iscsi.c` implements QEMU's iSCSI and iSER block protocol drivers using libiscsi. It connects to a remote target/LUN, probes SCSI capacity and capabilities, exposes the LUN as a `BlockDriverState`, and implements read, write, flush, discard, write-zeroes, block-status, SG_IO passthrough, copy-range via SCSI XCOPY, cache invalidation, reopen, truncate, and AioContext attach/detach.

## Main State

`IscsiLun` stores the driver instance state:
- libiscsi context,
- current AioContext,
- LUN number and SCSI device type,
- logical block size and block count,
- event masks and timers,
- mutex protecting libiscsi service/submission,
- logical block provisioning and block limit VPD data,
- saved device designator for XCOPY,
- zero block buffer for WRITE SAME,
- allocation bitmap/cache state,
- cluster size estimate,
- RW command width selection,
- write protection, provisioning, FUA, and WRITE SAME capability flags,
- request timeout/reconnect flag.

`IscsiTask` represents a coroutine-submitted SCSI command and carries status, retry state, returned `scsi_task`, coroutine pointer, error code/string, and retry timer.

On Linux, `IscsiAIOCB` supports asynchronous SG_IO passthrough and cancellation.

## Event Loop and Retry Model

libiscsi is integrated into QEMU's AioContext with fd handlers:
- `iscsi_set_events()` maps libiscsi's wanted `POLLIN`/`POLLOUT` events to QEMU fd handlers.
- `iscsi_process_read()` and `iscsi_process_write()` call `iscsi_service()` under the LUN mutex.
- `iscsi_timed_check_events()` periodically services timeout logic and triggers reconnect after timed-out requests.
- `iscsi_nop_timed_event()` sends NOP-Out probes and marks the connection for reconnect after too many in-flight NOPs.

`iscsi_co_generic_cb()` is the shared coroutine completion callback. It handles retryable statuses:
- `SCSI_STATUS_BUSY`,
- `SCSI_STATUS_TIMEOUT`,
- `SCSI_STATUS_TASK_SET_FULL`,
- check condition mapped to `EAGAIN`.

Retries use exponential random backoff based on `iscsi_retry_times`. Timeout status schedules retry after two event intervals and requests reconnect. The callback releases the LUN mutex before waking the coroutine to avoid direct wakeup deadlocks.

## Alignment and Sector Conversion

The driver converts between QEMU 512-byte sectors and target logical blocks with `sector_lun2qemu()` and `sector_qemu2lun()`. It rejects byte or sector requests not aligned to the target's logical block size. This is critical because SCSI READ/WRITE/UNMAP/WRITE SAME commands operate in LUN block units, not arbitrary bytes.

## Allocation Map and Sparse Zero Optimization

The driver maintains an optional allocation map when the target supports logical block provisioning and reports zeroes for unallocated blocks (`lbprz`). It uses:
- `allocmap`: whether a cluster is allocated,
- `allocmap_valid`: whether QEMU's knowledge is valid,
- `cluster_size`: guessed from optimal unmap granularity.

Reads can avoid network I/O when a valid cache entry says the range is unallocated and reads as zero. For larger reads over suspect unallocated areas, `iscsi_co_readv()` first calls `iscsi_co_block_status()` to query `GET LBA STATUS`; if the full request is zero, it fills the iovec locally.

Writes mark affected clusters allocated on success and invalid on failure. Discards and unmap-like zero writes invalidate or update the map depending on the command and flags. Reopen and cache invalidation reset allocation state.

## Read, Write, Flush

`iscsi_co_readv()` submits SCSI READ(10) or READ(16), using iov APIs when supported by the libiscsi version. It consults the allocation map first and zero-fills locally when safe.

`iscsi_co_writev()` submits SCSI WRITE(10) or WRITE(16), optionally with FUA if the target advertises DPOFUA. It validates max transfer assumptions, updates allocation map state, and reports libiscsi/SCSI errors through QEMU error reporting.

`iscsi_co_flush()` sends SYNCHRONIZE CACHE(10). The driver registers this as `.bdrv_co_flush_to_disk`.

## Block Status, Discard, and Zero Writes

`iscsi_co_block_status()` defaults to allocated data if logical block provisioning is absent or status query fails. When supported, it sends GET LBA STATUS and maps deallocated/anchored provisioning descriptors to non-data, and to `BDRV_BLOCK_ZERO` when the target has `lbprz`.

`iscsi_co_pdiscard()` implements UNMAP if `lbpu` is advertised. It silently tolerates check condition for target alignment dissatisfaction and invalidates the allocation map for the discarded range.

`iscsi_co_pwrite_zeroes()` implements WRITE SAME(10/16), optionally with UNMAP. It chooses WRITE SAME(16) when needed for unmap support or when normal RW uses 16-byte commands. If the target rejects WRITE SAME with invalid operation/code-field sense, the driver disables `has_write_same` and returns `-ENOTSUP`.

## SG_IO Passthrough on Linux

Under `__linux__`, the driver implements `.bdrv_aio_ioctl`:
- non-`SG_IO` requests emulate `SG_GET_VERSION_NUM` and `SG_GET_SCSI_ID`,
- `SG_IO` builds a libiscsi `scsi_task` from the user CDB,
- supports direct buffers or iovec transfer,
- maps check condition sense data back into `sg_io_hdr_t`,
- supports async cancellation with iSCSI task management abort.

This is important for non-disk/ROM SCSI device types, which are exposed as sg-compatible devices.

## Opening and Probing

`iscsi_parse_filename()` parses URLs of the form `iscsi://[user%password@]host[:port]/target/lun`, sets runtime QDict options, applies `-iscsi` defaults, and honors URL credentials if provided.

`iscsi_open()`:
- absorbs runtime options,
- validates transport/portal/target,
- creates libiscsi context using an initiator name from options, VM UUID, or VM name,
- initializes TCP/iSER transport,
- applies target name, CHAP, session type, header digest, and timeout,
- connects to the LUN,
- performs standard inquiry to determine device type,
- performs MODE SENSE for write protection and DPOFUA,
- applies auto-read-only if needed,
- reads capacity,
- marks non-disk/non-ROM devices as SG devices,
- probes supported VPD pages for logical block provisioning, block limits, and device identification,
- attaches AioContext handlers/timers,
- initializes allocation map if useful,
- sets supported zero/FUA flags.

`iscsi_close()` detaches the AioContext, logs out, destroys the libiscsi context, frees designator/zero/bitmap memory, destroys the mutex, and clears instance state.

## Limits and Reopen/Truncate

`iscsi_refresh_limits()` exports target-derived constraints:
- request alignment equals at least the LUN block size,
- max transfer derives from READ/WRITE(10/16) and block limits,
- discard maximum/alignment derives from UNMAP limits,
- write-zeroes maximum/alignment derives from WRITE SAME and provisioning limits,
- optimal transfer is rounded down to a power of two.

`iscsi_reopen_prepare()` refuses read-write reopen on write-protected LUNs. `iscsi_reopen_commit()` rebuilds the allocation map when cache.direct status changes.

`iscsi_co_truncate()` cannot actually resize iSCSI devices. It refreshes capacity and allows no-op/non-exact shrink-style checks, but rejects exact size changes and growth.

## Copy Range via XCOPY

The driver supports copy range between compatible iSCSI-backed nodes using SCSI EXTENDED COPY:
- both source and destination must be this driver's copy-range implementation,
- both LUNs need saved device designators,
- offsets and length must be aligned,
- block sizes must match,
- transfer length must fit XCOPY's 16-bit block count.

Helper functions build target descriptors, block-to-block segment descriptors, the parameter header, and the EXTENDED COPY task. `iscsi_co_copy_range_to()` submits the command to the destination LUN and traces the result.

## Driver Registration

The file registers `bdrv_iscsi` unconditionally when built with libiscsi. With libiscsi API support for transports, it also registers `bdrv_iser`. Both drivers expose the same operations and strong runtime options.
