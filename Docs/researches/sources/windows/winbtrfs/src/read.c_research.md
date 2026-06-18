# File Research: sources/windows/winbtrfs/src/read.c

## Purpose

`read.c` implements the WinBtrfs filesystem driver read path. It covers checksum calculation/verification, logical-to-physical reads across Btrfs chunk profiles, degraded and checksum-error recovery for mirrored and parity layouts, compressed extent handling, alternate data stream reads, cache manager integration, and the `IRP_MJ_READ` dispatch routine.

This file is central to correctness: it decides which devices to read from, validates returned data against Btrfs checksums and tree headers, repairs bad mirrors/parity members when possible, decompresses file data, fills holes with zeroes, and bridges Windows IRP/cache-manager behavior to Btrfs extent storage.

## Main Data Structures

- `enum read_data_status`: tracks each physical stripe request as pending, success, error, missing device, or skipped.
- `read_data_stripe`: per-stripe read state, including associated IRP, IOSB, MDL, stripe number, and physical stripe byte range.
- `read_data_context`: shared context for a logical read across devices; owns the completion event, stripe array, checksum pointer, target chunk/profile type, sector geometry, and optional temporary virtual address buffer.
- `read_part_extent`: describes one logical file extent segment inside a coalesced compressed read.
- `read_part`: queued physical read work for `read_file`; records disk address, chunk, checksum data, target buffer, compression, and one or more extent fragments.
- `comp_calc_job`: tracks asynchronous decompression jobs scheduled via the calculation thread infrastructure.

## Checksum Helpers

`check_csum` allocates a temporary checksum buffer, calls `do_calc_job`, and compares all sector checksums. It returns `STATUS_CRC_ERROR` on mismatch and propagates allocation failures.

`get_tree_checksum` and `check_tree_checksum` implement tree-block checksum support for CRC32C, XXHASH, SHA256, and BLAKE2. Tree checksum inputs begin at `tree_header.fs_uuid`, excluding the stored checksum field. `check_tree_checksum` logs expected/actual values for CRC32C and XXHASH and returns false for mismatch.

`get_sector_csum` and `check_sector_csum` perform the same checksum-family selection for one filesystem sector. These helpers are used when isolating which sector inside a larger read failed validation.

## Physical Read Completion

`read_data_completion` is the lower-device IRP completion routine. It copies `Irp->IoStatus` into the stripe state, maps success/failure to `ReadDataStatus_Success` or `ReadDataStatus_Error`, decrements the shared `stripes_left`, signals the event when all submitted reads complete, and returns `STATUS_MORE_PROCESSING_REQUIRED` so the caller retains control of associated IRP cleanup.

## Chunk Profile Read/Recovery Helpers

`read_data_dup` handles SINGLE, DUP, RAID1, RAID1C3, and RAID1C4-style mirrored reads. It selects the first successful stripe, verifies either tree metadata or file checksums, and if corrupted, attempts to reread alternate mirrors. On successful recovery it copies good data into the caller buffer and, when the volume and target device are writable, writes the good sector/tree back to the bad mirror. It logs Btrfs device stats for read, corruption, generation, and write errors.

`read_data_raid0` validates non-redundant striped reads. It cannot recover: stripe read errors or checksum/tree-header mismatches become hard failures. It maps failed sectors back to the physical RAID0 stripe with `get_raid0_offset` for device error accounting.

`read_data_raid10` combines RAID0 placement with mirrored substripes. It validates the selected mirror and, on checksum/tree-generation failure, rereads another mirror in the same substripe set. It can rewrite recovered tree blocks or sectors to the bad mirror when allowed.

`read_data_raid5` validates and reconstructs RAID5 data. It first overlays in-memory `partial_stripe` data from the chunk when present, protecting reads that overlap pending parity-stripe updates. On checksum failure or degraded mode, it reconstructs missing/bad tree blocks or sectors by XORing all other stripes. It supports repair writeback to the failed/corrupt device when writable.

`raid6_recover2` reconstructs two missing RAID6 stripes using P/Q parity and Galois-field math. It supports the case where one missing stripe is P parity, and the general case using P and Q equations.

`read_data_raid6` extends RAID5 logic to dual-parity layouts. It overlays partial stripes, validates checksums/tree metadata, reconstructs with XOR when possible, falls back to Q-parity-assisted two-error recovery, identifies parity versus data corruption, and writes repaired data/parity back to devices when allowed. It permits up to two missing devices.

## `read_data` Logical-to-Physical Read Engine

`read_data` is the main block-layer read function. Inputs include a logical address, length, optional checksums, tree/read flags, output buffer, optional known chunk, optional parent IRP, expected tree generation, whether the destination is a file-read buffer, and MDL mapping priority.

Important behavior:

- Resolves the containing chunk either from `Vcb->log_to_phys_loaded` chunk mapping or bootstrap `Vcb->sys_chunks`.
- Classifies the chunk profile into DUP/SINGLE/RAID1/RAID1C3/RAID1C4, RAID0, RAID10, RAID5, or RAID6 and sets `allowed_missing`.
- Allocates `read_data_context.stripes`.
- Locks RAID5/RAID6 chunk ranges with `chunk_lock_range` to coordinate with partial stripe state.
- Builds per-stripe MDLs and byte ranges differently for RAID0, RAID10, DUP/mirrors, RAID5, and RAID6.
- Uses a temporary `context.va` for file reads when direct deinterlacing or checksum validation cannot safely operate against caller MDLs.
- Uses dummy pages for parity stripes in long RAID5/RAID6 reads so MDL layouts remain valid while skipping parity data.
- Marks absent devices or empty stripe ranges as `ReadDataStatus_MissingDevice` and fails if missing count exceeds redundancy.
- Allocates lower read IRPs or associated IRPs, sets buffered/direct/neither I/O fields according to the lower device flags, installs `read_data_completion`, submits all active stripes, and waits for completion.
- Updates disk counters when `diskacc` is enabled.
- Short-circuits user-induced lower-device errors before attempting checksum recovery.
- Dispatches post-read validation/recovery to the profile-specific helper.
- Copies temporary file-read buffers back to the caller after successful validation.
- Cleans up RAID locks, dummy MDL/page, per-stripe MDLs/IRPs, temporary bootstrap device arrays, and stripe context.

A notable implementation detail is the use of MDL page-frame manipulation for RAID0/RAID10/RAID5/RAID6 deinterlacing. Comments acknowledge that MDLs are officially opaque and this could break on future Windows versions.

## File and Stream Reads

`read_stream` handles alternate data streams stored in-memory in `fcb->adsdata`. It checks EOF and zero-length reads, copies the available range, and reports bytes read.

`read_file` handles normal Btrfs file extents:

- Rejects reads starting beyond `inode_item.st_size`.
- Walks `fcb->extents` fully in logical order.
- Fills holes between extents with zeroes.
- Rejects unsupported encryption and nonzero encoding.
- Handles inline extents:
  - Raw inline data is copied directly.
  - ZLIB, LZO, and ZSTD inline data are decompressed, with an intermediate buffer when reading from a nonzero offset.
- Handles regular extents:
  - Builds `read_part` entries with physical address, aligned read length, checksum pointer, target copy offset, compression type, and chunk pointer.
  - Uses direct target buffers only for uncompressed sector-aligned reads; otherwise allocates a temporary buffer.
- Handles preallocated extents by returning zeroes.
- Merges adjacent compressed `read_part` entries when they are contiguous, same compression, same chunk, adjacent destination, and compatible checksum state. The merged structure carries multiple `read_part_extent` fragments and may allocate a combined checksum buffer.
- Calls `read_data` for every queued physical read part.
- Copies uncompressed temporary buffers back to the destination when needed.
- For compressed regular extents, prepares decompression jobs using `add_calc_job_decomp`; LZO handling skips page-compressed chunks until the requested offset.
- Runs queued decompression jobs with `calc_thread_main`, waits on their events, copies decompressed slices into the output, and frees temporary buffers.
- Zero-fills trailing sparse data up to file size.
- Cleans all pending read parts and decompression jobs on exit.

The decompression code intentionally avoids decompressing directly into final mmap-backed destinations because Windows may use dummy pages that can break algorithms requiring backtracking, especially ZSTD.

## Windows Read Path

`do_read` is the core IRP read implementation after `drv_read` has validated the file object and acquired locks.

It rejects directory reads except ADS reads, checks byte-range locks for non-paging I/O, handles zero-length and EOF reads, and maps the user buffer. It respects `ValidDataLength`: reads beyond valid data are zero-filled, and reads crossing VDL append zeroes for the tail.

For cached reads, it initializes the cache map when needed and uses `CcMdlRead`, `CcCopyReadEx`, or `CcCopyRead`. If the cache manager cannot wait, the IRP is marked pending. For noncached reads, it requires synchronous wait, then calls `read_stream` for ADS or `read_file` for regular file data. It updates `Irp->IoStatus.Information` and process disk counters when enabled.

`drv_read` is the `IRP_MJ_READ` dispatch entry point. It:

- Enters the filesystem with `FsRtlEnterFileSystem` and top-level IRP tracking.
- For volume device objects, delegates to `vol_read`.
- Handles `IRP_MN_COMPLETE` by calling `CcMdlReadComplete`.
- Validates `fcb`, `ccb`, and `FILE_READ_DATA` access for user-mode callers.
- Passes reads against the volume FCB through to the real device.
- Checks oplocks for non-paging I/O.
- Forces synchronous handling for paging I/O to avoid deadlocks in `CcCopyRead`.
- Flushes mapped cached data before non-paging reads when a data section exists.
- Acquires the FCB resource shared if not already held.
- Calls `do_read`, updates synchronous file-object current byte offset, completes non-pending IRPs, or queues pending work with `add_thread_job` and falls back to `do_read_job`.
- Restores top-level IRP state and exits the filesystem.

## Dependencies and Cross-File Interactions

This file depends heavily on declarations and helpers from `btrfs_drv.h`, checksum code from `crc32c.h`, XXHASH from the bundled ZSTD sources, compression helpers (`zlib_decompress`, `lzo_decompress`, `zstd_decompress`), Btrfs chunk geometry helpers (`get_raid0_offset`, `get_raid56_lock_range`), lower-device I/O helpers (`sync_read_phys`, `write_data_phys`), device error accounting (`log_device_error`), cache initialization, calculation-thread jobs, and worker-thread queuing.

It also interacts with FCB/CCB state, file extents, chunk/device mappings, partial-stripe tracking, Windows Cache Manager, MDLs, IRPs, oplocks, byte-range locks, and process disk counters.

## Error Handling and Safety Notes

Most allocation and lower-I/O failures return NTSTATUS codes directly after logging. Redundant profiles aggressively attempt checksum recovery and repair writeback, while RAID0 and SINGLE without alternate copies cannot recover. The code distinguishes corruption errors from generation mismatches for metadata reads.

Cleanup is centralized in `read_data` and `read_file`, but the paths are complex. Important invariants include correct MDL lock/unlock handling, freeing temporary file-read buffers exactly once, preserving RAID locks around parity reads, and not dereferencing absent devices in degraded paths.

## Research Notes

This file should be studied with the write path and chunk/extent-tree code because read recovery can write repaired data back to devices and must coordinate with partial stripe state. It is also a useful map of how WinBtrfs adapts Btrfs extent/chunk semantics to Windows IRP, MDL, and cache-manager mechanics.
