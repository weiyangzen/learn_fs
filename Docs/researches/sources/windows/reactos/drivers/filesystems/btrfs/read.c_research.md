# File Research: sources/windows/reactos/drivers/filesystems/btrfs/read.c

## Purpose

`read.c` implements the WinBtrfs read path for ReactOS, spanning physical chunk reads, checksum validation, profile-specific redundancy recovery, extent decoding, cache manager integration, and the IRP dispatch handler for `IRP_MJ_READ`.

It is central to Btrfs data integrity: reads are not just block transfers, but profile-aware operations that may verify checksums, reconstruct data from mirrors/parity, repair corrupt copies, and translate Btrfs extents into Windows file reads.

## Main Responsibilities

- Issue physical read IRPs against one or more backing devices.
- Verify tree and data checksums using CRC32C, xxHash, SHA-256, or BLAKE2.
- Handle Btrfs chunk profiles:
  - single/duplicate/RAID1/RAID1C3/RAID1C4 via duplicate read logic
  - RAID0 striping
  - RAID10 mirrored striping
  - RAID5 parity reconstruction
  - RAID6 dual-parity reconstruction
- Recover from checksum or missing-device failures when possible.
- Write repaired data back to bad devices when the filesystem/device is writable.
- Read inline, regular, preallocated, sparse, compressed, and alternate data stream content.
- Integrate with Windows cache manager paths such as `CcCopyRead`, `CcCopyReadEx`, `CcMdlRead`, and direct noncached reads.
- Dispatch and complete filesystem read IRPs.

## Key Types

- `enum read_data_status`: tracks per-stripe state: pending, success, error, missing device, or skipped.
- `read_data_stripe`: records one physical stripe read, including IRP, MDL, status, stripe offset range, and completion status.
- `read_data_context`: shared state for a logical `read_data` operation: chunk, target address, checksum pointer, stripe list, sector size, read buffer, and synchronization event.
- `read_part`: describes a file extent fragment that must be read from disk, including checksum, compression, chunk pointer, buffer ownership, and extent slices.
- `read_part_extent`: records logical subranges inside merged compressed read parts.
- `comp_calc_job`: tracks asynchronous decompression jobs and the destination copy range.

## Important Functions

- `read_data_completion`: completion routine for physical stripe read IRPs. It stores `IoStatus`, marks success/error, decrements the shared stripe counter, and signals the event when all reads complete.
- `check_csum`: computes checksums over multiple sectors and compares them with supplied checksum bytes.
- `get_tree_checksum`, `check_tree_checksum`: compute and verify Btrfs tree block checksums for all supported checksum algorithms.
- `get_sector_csum`, `check_sector_csum`: compute and verify one sector checksum.
- `read_data_dup`: handles single, duplicate, RAID1, RAID1C3, and RAID1C4-like reads. It chooses a successful mirror, verifies it, then tries alternate mirrors for corrupt tree/data sectors and repairs the bad mirror if possible.
- `read_data_raid0`: validates striped reads. RAID0 has no redundancy, so checksum failures are logged as unrecoverable.
- `read_data_raid10`: verifies chosen mirror stripes and recovers from alternate sub-stripes when checksum validation fails.
- `read_data_raid5`: handles RAID5 verification and reconstruction from parity, including partial stripe overlays from in-memory write state.
- `raid6_recover2`: reconstructs RAID6 missing/corrupt stripes using P/Q parity and Galois field arithmetic.
- `read_data_raid6`: handles RAID6 verification, missing-device recovery, checksum recovery, and parity repair.
- `read_data`: top-level physical/logical chunk read routine. It finds the chunk, maps logical ranges to physical stripes, builds MDLs/IRPs, waits for completion, validates/reconstructs data, cleans up MDLs/IRPs, and returns status.
- `read_stream`: reads an alternate data stream stored in memory in `fcb->adsdata`.
- `read_file`: reads logical file contents from the extent list, handling sparse holes, inline extents, regular extents, preallocation, compression, checksum lookup, merged compressed reads, and decompression.
- `do_read`: handles one filesystem read IRP after locking, choosing cached, MDL, ADS, or noncached file-read paths.
- `drv_read`: registered `IRP_MJ_READ` dispatch entry point. It validates state/access, handles volume reads, oplocks, cache flushes, resource locking, pending work queue fallback, and IRP completion.

## Physical Read Flow

`read_data` first resolves the logical address to a Btrfs chunk. If the log-to-physical map is loaded, it uses `get_chunk_from_address`; during bootstrap it scans `Vcb->sys_chunks` and builds a temporary device array.

It normalizes chunk flags into a smaller set of read strategies:

- duplicate-like: single, duplicate, RAID1, RAID1C3, RAID1C4
- RAID0
- RAID10
- RAID5
- RAID6

It then computes allowed missing devices, allocates per-stripe context, optionally locks RAID5/6 stripe ranges, and builds MDLs. For stripe profiles, the code constructs per-device MDLs by copying page frame numbers from a master MDL into stripe-specific MDLs. This is a deliberate Windows-kernel optimization to avoid extra data copying, but it relies on MDL layout assumptions noted by comments in the file.

After IRPs are submitted with `IoCallDriver`, `read_data` waits on the shared event and checks for user-induced errors. The profile-specific validator then verifies checksums and reconstructs or repairs as needed.

## Integrity and Recovery Behavior

Tree blocks are verified by checksum, logical address, and optionally generation. Data extents are verified sector-by-sector when checksums are available.

Recovery strategy depends on chunk profile:

- Duplicate/mirror profiles read alternate copies and copy good data into the output buffer.
- RAID10 tries alternate sub-stripes within the mirrored stripe set.
- RAID5 reconstructs missing or corrupt sectors by XORing remaining stripes.
- RAID6 reconstructs using P/Q parity and can handle two missing/corrupt stripes in supported cases.
- RAID0 cannot recover checksum failures.

When recovery succeeds and the filesystem is writable, the code attempts to write the repaired block or sector back to the bad device. It logs device statistics for read, write, corruption, and generation errors.

## File Extent Read Flow

`read_file` walks `fcb->extents` and materializes logical file contents into the caller buffer:

- Gaps are zero-filled.
- Inline uncompressed extents are copied directly.
- Inline compressed extents are decompressed from inline data.
- Regular extents become `read_part` entries, with sector alignment and checksum selection.
- Preallocated extents read as zeroes.
- Unsupported encryption or encoding returns `STATUS_NOT_IMPLEMENTED`.

For compressed regular extents, adjacent compatible read parts can be merged to reduce I/O. After disk reads complete, compressed buffers are decompressed through `add_calc_job_decomp` and `calc_thread_main`, then copied into the final destination.

Supported compression paths include zlib, LZO, and ZSTD. LZO has special page/block skipping logic for reads into the middle of compressed data.

## Windows Read Integration

`do_read` implements policy around Windows read semantics:

- Rejects directory reads except ADS reads.
- Enforces byte-range locks for non-paging I/O.
- Handles EOF and valid-data-length zero fill.
- Uses `CcMdlRead` for cached MDL reads.
- Uses `CcCopyReadEx` when available, falling back to `CcCopyRead`.
- Handles noncached reads through `read_stream` or `read_file`.
- Updates disk counters for user-visible reads when enabled.

`drv_read` wraps this with filesystem dispatch concerns: top-level IRP state, volume passthrough reads, MDL read completion, access checks, oplock checks, cache flushes for mapped sections, FCB resource locking, synchronous/asynchronous wait handling, pending job queue fallback, and final IRP completion.

## Notable Risks and Implementation Notes

- The RAID0/RAID10/RAID5/RAID6 MDL manipulation depends on PFNs following the MDL structure in memory. The code explicitly notes that MDLs are officially opaque and this could break on future Windows versions.
- Several cleanup paths rely on the common `exit:` block. Resource ownership is complex because `context.va`, stripe MDLs, dummy MDLs, IRPs, temporary device arrays, and RAID locks are conditionally allocated.
- SHA-256 and BLAKE2 tree checksum comparisons appear to compare computed hashes against `th` rather than `th->csum` in `check_tree_checksum`; this is worth auditing against upstream WinBtrfs history because it may be intentional only if structure layout makes it equivalent, but it reads suspiciously.
- RAID56 code overlays in-memory partial stripes before checksum validation, which is important for consistency with pending writes.
- Compression reads avoid decompressing directly into mmap-backed destination pages because Windows may use dummy pages that break decompressor backtracking.
- The path intentionally treats some user-induced device errors specially before attempting redundancy recovery.
