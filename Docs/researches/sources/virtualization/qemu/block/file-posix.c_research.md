# File Research: sources/virtualization/qemu/block/file-posix.c

## Purpose
POSIX implementation of QEMU's raw `file`, `host_device`, and platform-specific `host_cdrom` block protocol drivers. It is the main Unix host file/device backend for block I/O, covering regular files, block devices, character devices, SCSI generic passthrough, direct I/O alignment, page-cache handling, sparse allocation queries, discard/write-zeroes, copy offload, zoned devices, permissions, and file creation.

## Main State
`BDRVRawState` stores:
- Host file descriptor and open flags.
- File/device type.
- Locking mode and current/shared block permissions.
- Byte-lock bookkeeping for QEMU permission enforcement.
- Reopen/permission-change fd state.
- AIO backend flags: Linux AIO, io_uring, AIO batch size, `fdatasync` support.
- Capabilities for discard, write-zeroes, fallocate.
- Alignment state: request alignment, buffer alignment, forced alignment.
- Live migration cache-drop options.
- Discard statistics.
- Optional persistent reservation manager.

`RawPosixAIOData` is the thread-pool/native-AIO work packet for read/write, flush, ioctl, copy-range, truncate, zone report, and zone management operations.

## Opening and Options
`raw_open_common()` handles most open logic for both regular files and host devices:
- Parses `filename`, `aio`, `aio-max-batch`, `locking`, `pr-manager`, `drop-cache`, and `x-check-cache-dropped`.
- Supports `aio=threads`, `aio=native`, and, when built, `aio=io_uring`.
- Requires `cache.direct=on` for Linux native AIO.
- Checks io_uring availability when requested.
- Applies auto-read-only logic via `raw_parse_flags()`.
- Opens the path, checks writable block-device state with `BLKROGET`, validates file type, initializes discard/write-zeroes capabilities, and sets block-layer supported flags.
- Rejects non-regular files for the `file` driver and non-device files for host-device mode.
- For zoned devices, rejects buffered I/O because host page cache cannot preserve required write ordering.

## Alignment Handling
- Probes logical block size through available ioctls.
- Probes physical block size when possible.
- Detects direct-I/O request and memory alignment by issuing trial reads.
- Special-cases NFS as byte-aligned for direct I/O.
- Falls back to conservative alignment when probing cannot provide exact data.
- Exposes `min_mem_alignment`, `opt_mem_alignment`, request alignment, discard alignment, and write-zeroes alignment to the block layer.

## Permission and Locking Model
The driver maps QEMU block permissions to byte-range locks:
- Permission lock bytes start at `RAW_LOCK_PERM_BASE`.
- Shared-permission lock bytes start at `RAW_LOCK_SHARED_BASE`.
- `raw_apply_lock_bytes()` locks/unlocks bytes.
- `raw_check_lock_bytes()` probes conflicting locks from other processes.
- `raw_handle_perm_lock()` implements prepare/commit/abort around permission updates.
- Reopen can duplicate or reopen the fd and transfer locks to the replacement fd in `raw_check_perm()` / `raw_set_perm()`.

## I/O Path
`raw_co_prw()` is the central read/write path:
- Checks fd validity.
- For zoned writes/appends, serializes through zone write-pointer mutex and updates tracked write pointers.
- Uses io_uring when enabled and aligned.
- Uses Linux AIO when enabled, available, and aligned.
- Falls back to the coroutine thread pool.
- Thread-pool read/write uses `preadv/pwritev` when available, otherwise linearizes iovecs into aligned buffers.
- Short reads are zero-filled; short writes return error.
- FUA write requests are followed by flush when the selected backend cannot provide native FUA.

## Flush and Page Cache
- `raw_co_flush_to_disk()` uses io_uring, Linux AIO fdatasync, or thread-pool `qemu_fdatasync()`.
- Failed buffered `fdatasync()` marks `page_cache_inconsistent`, causing future flushes to fail permanently because dirty pages may have been lost.
- `raw_co_invalidate_cache()` flushes and uses `posix_fadvise(..., DONTNEED)` on Linux when `drop-cache` is enabled and not using `O_DIRECT`.
- Optional `x-check-cache-dropped` verifies cache eviction via `mincore()`.

## Allocation, Creation, and Truncation
- `raw_co_create()` creates files with optional `nocow`, preallocation, and extent-size hint.
- Uses permission locks during creation to prevent conflicting resize/write access.
- Supports preallocation modes `off`, `full`, and optionally `falloc`.
- Uses `FS_NOCOW_FL` where available for btrfs-like behavior.
- Uses `FS_IOC_FSSETXATTR` to set extent-size hints when supported.
- `raw_regular_truncate()` delegates blocking truncate/preallocate work to the thread pool.
- `find_allocation()` uses `SEEK_DATA`/`SEEK_HOLE` where available.
- `raw_co_block_status()` reports data/zero extents and treats unknown sparse info conservatively as data.

## Discard, Write Zeroes, and Copy Offload
- Regular-file discard uses `fallocate(PUNCH_HOLE|KEEP_SIZE)` where available, or macOS `F_PUNCHHOLE`.
- Block-device discard uses `BLKDISCARD`.
- Block-device write-zeroes uses `BLKZEROOUT` when allowed.
- Regular-file write-zeroes tries `FALLOC_FL_ZERO_RANGE`, hole punching plus reallocation, or fallocate extension.
- `BDRV_REQ_MAY_UNMAP` selects the unmap-capable write-zeroes path.
- Discard successes/failures and discarded bytes are tracked in file-specific stats.
- `raw_co_copy_range_to()` uses host `copy_file_range()` only when both source and destination are the raw POSIX driver.

## Zoned Device Support
When `CONFIG_BLKZONED` is enabled:
- Reads zoned model and limits from sysfs.
- Tracks zone size, number of zones, max open/active zones, max append sectors, and write granularity.
- Maintains in-memory zone write pointers.
- Implements zone report using `BLKREPORTZONE`.
- Implements open/close/finish/reset through Linux zone ioctls.
- Implements zone append through the normal write path with write-pointer updates.
- Resets or refreshes tracked write pointers after zone-management operations and failed writes.

## Host Device Support
When `HAVE_HOST_BLOCK_DEVICE` is enabled:
- `hdev_probe_device()` recognizes character and block devices.
- `hdev_open()` opens device mode, detects Linux SCSI generic devices, and disables dm-multipath SG_IO retry logic for SG devices.
- Linux SG_IO supports persistent reservations via `PRManager` for `PERSISTENT_RESERVE_IN/OUT`.
- dm-multipath retry handling probes paths with `DM_MPATH_PROBE_PATHS`, retries transient `EAGAIN`, and classifies SG_IO path errors.
- Host-device block ops reuse raw read/write/flush/copy/truncate/length paths and add block-size and geometry probes.
- Host-device discard/write-zeroes set a block-device flag so ioctl paths are used.

## CD-ROM Support
- Linux `host_cdrom` opens with `O_NONBLOCK`, detects CD drives via `CDROM_DRIVE_STATUS`, supports inserted/eject/close-tray/lock-door ioctls, and exposes SG_IO.
- FreeBSD `host_cdrom` opens through raw device logic, unlocks the door, can reopen after media changes, and supports inserted/eject/lock operations.
- macOS helper code maps `/dev/cdrom` to an ejectable optical media BSD path using IOKit and emits unmount/remount guidance when needed.

## Registered Drivers
- Always registers `bdrv_file`.
- Registers `bdrv_host_device` when host block devices are enabled.
- Registers `bdrv_host_cdrom` on Linux and FreeBSD variants when available.
- Registration order intentionally matters because later drivers are probed first.

## Important Interactions
- This file is a foundational backend for higher-level block formats and exports.
- Export drivers in this group ultimately depend on these raw file/device protocol drivers when their `BlockBackend` points at local host storage.
- Permission locking is advisory and only works between cooperating QEMU-like processes using the same byte-lock convention.
