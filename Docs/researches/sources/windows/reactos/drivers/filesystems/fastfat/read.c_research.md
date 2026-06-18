# File Research: sources/windows/reactos/drivers/filesystems/fastfat/read.c

This file implements FastFAT `IRP_MJ_READ` handling for user files, directories, EA files, volume/DASD handles, virtual volume file reads, paging-file reads, cached reads, noncached reads, MDL reads, and low-stack overflow recovery.

Key responsibilities:
- Dispatch reads through `FatFsdRead` and `FatCommonRead`.
- Fast-path paging-file reads directly to `FatPagingFileIo`.
- Post low-stack reads to filesystem stack-overflow workers.
- Decode file-object open type and route read behavior accordingly.
- Enforce EOF, valid-data-length, sector-alignment, locking, oplock, cache, and DASD rules.
- Initialize `FAT_IO_CONTEXT` for noncached I/O.
- Maintain per-processor read statistics.
- Update synchronous file positions and mark successful nonpaging reads for access-time update.

Important functions:
- `FatFsdRead`: top-level read dispatch, including paging-file fast path, MDL-complete handling, low-stack detection, IRP context creation, and exception processing.
- `FatPostStackOverflowRead`: preacquires the resource needed by the read path, posts the read to `FsRtlPostStackOverflow`, and waits until the worker has started/completed the protected section.
- `FatStackOverflowRead`: runs `FatCommonRead` with wait semantics on a safer stack, including verify-thread substitution when needed.
- `FatCommonRead`: main read engine.
- `FatOverflowPagingFileRead`: stack-overflow helper for paging-file reads.

Main read flows:
- Zero-length reads complete successfully with zero information.
- `UserVolumeOpen` and `VirtualVolumeFile` reads become noncached LBO reads through `FatSingleAsync`.
- DASD reads verify the VCB unless complete-dismount or format-unit flags allow bypass, flush the volume once per CCB, trim to volume size unless extended DASD I/O is allowed, and lock the user buffer.
- Normal user-file reads acquire the FCB or paging I/O resource, check oplocks and byte-range locks, trim to file size, then choose cached or noncached transfer.
- Noncached user-file reads zero data beyond valid data length, reduce physical I/O to VDL, round physical reads to sector boundaries, and use special handling for unaligned reads.
- Cached user-file reads lazily initialize the cache map, verify allocation size, use `CcCopyRead`/`CcCopyReadEx`, or `CcMdlRead` for MDL reads.
- Directory and EA file reads are expected to be noncached paging I/O, sector aligned, and within allocation size.
- User directory reads fail with `STATUS_INVALID_PARAMETER`.

Important interactions:
- Uses `FatAcquireSharedFcb`, `FatAcquireSharedFcbWaitForEx`, and paging I/O resources depending on read type.
- Uses `FsRtlCheckOplock` and `FsRtlCheckLockForReadAccess` for nonpaging file reads.
- Uses `CcFlushCache` before noncached reads when a data section exists, avoiding stale cached data.
- Uses `FatNonCachedIo`, `FatNonCachedNonAlignedRead`, `FatSingleAsync`, and `FatWaitSync` for physical I/O.
- Uses `FatMapUserBuffer`, `FatLockUserBuffer`, and guarded zeroing for user buffers.

Notable behavior and risks:
- Reads with nonzero high offset parts on regular files return EOF because FAT file sizes are 32-bit.
- Noncached reads that extend past VDL may partially zero the caller buffer while only physically reading valid sectors.
- Async noncached reads may detach the IRP context and return `STATUS_PENDING`.
- Stack-allocated `FAT_IO_CONTEXT` cleanup must free any zero MDL before returning on exceptional paths.
