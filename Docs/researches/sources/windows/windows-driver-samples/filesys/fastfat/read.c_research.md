# File Research: sources/windows/windows-driver-samples/filesys/fastfat/read.c

## Purpose
Implements all FastFAT read handling: dispatch entry, stack-overflow fallback, paging-file reads, cached reads, noncached reads, volume reads, directory/EA metadata reads, MDL reads, EOF/VDL trimming, and completion behavior.

## Main Entry Points
- `FatFsdRead`: dispatch routine for `IRP_MJ_READ`.
- `FatCommonRead`: common read implementation for FSD/FSP paths.
- `FatPostStackOverflowRead`: posts low-stack reads to a special stack-overflow worker.
- `FatStackOverflowRead`: worker routine for posted low-stack reads.
- `FatOverflowPagingFileRead`: low-stack paging-file read worker.

## Dispatch Behavior
`FatFsdRead` first handles paging-file I/O as a special fast path before creating an IRP context. Paging-file reads are marked pending and sent to `FatPagingFileIo`, or posted to `FsRtlPostPagingFileStackOverflow` when remaining stack is below `OVERFLOW_READ_THRESHHOLD`.

For normal reads it sets top-level IRP state, creates an IRP context, handles MDL-complete requests through `FatCompleteMdl`, checks for stack overflow risk, and calls `FatCommonRead`.

## Stack Overflow Handling
`FatPostStackOverflowRead` preacquires the resource that `FatCommonRead` will need, prepares the IRP for posting, marks verify-read context when needed, posts to `FsRtlPostStackOverflow`, waits for the worker to reach the safe point, then releases the preacquired resource.

`FatStackOverflowRead` forces waitable processing, temporarily substitutes `Vcb->VerifyThread` for verify-driven reads, calls `FatCommonRead`, maps `STATUS_FILE_DELETED` to EOF in that special path, restores verify-thread state, and signals the waiting event.

## Read Classification
`FatCommonRead` decodes the file object into:
- `VirtualVolumeFile`
- `UserVolumeOpen`
- `UserFileOpen`
- `DirectoryFile`
- `EaFile`
- `UserDirectoryOpen`

Zero-length reads complete immediately with success.

Raw volume opens are forced noncached. Virtual volume reads and user volume reads are translated to LBO-based lower-device reads with `FatSingleAsync`.

User directory opens reject read with `STATUS_INVALID_PARAMETER`.

## User Volume Reads
For `UserVolumeOpen`, the code:
- Verifies the VCB unless the CCB indicates complete dismount or format-unit state.
- Sets override-verify for format-unit follow-up I/O.
- Performs a one-time DASD flush unless the volume is locked.
- Trims reads to volume size unless extended DASD I/O is allowed.
- Locks the user buffer and sends one async lower-device read.
- Updates disk accounting on newer Windows when enabled.
- Updates current byte offset for synchronous nonpaging reads.

## User File Reads
For user files, the code:
- Rejects high-part offsets beyond FAT’s supported range with EOF.
- Flushes cached data before noncached nonpaging reads when a data section exists.
- Acquires paging I/O resource for paging reads, otherwise the main FCB resource.
- Uses `FatAcquireSharedFcbWaitForEx` for async noncached reads to avoid starving exclusive waiters.
- Verifies the FCB.
- Checks oplocks for nonpaging reads.
- Checks byte-range locks via `FsRtlCheckLockForReadAccess`.
- Trims reads to file size and treats reads starting at or beyond EOF as EOF.

## Noncached User File Reads
The noncached path:
- Determines sector size.
- Raises effective VDL to at least `ValidDataToDisk`.
- Zeroes portions beyond valid data length.
- Completes entirely from zeroing if the read starts beyond VDL.
- Trims physical read length to VDL, then rounds to sector boundary.
- Uses `FatNonCachedNonAlignedRead` for misaligned reads or when sector rounding would exceed caller buffer length.
- Uses `FatNonCachedIo` for aligned reads.
- Reports the original requested byte count constrained to file size, not just the physical byte count.

## Cached And MDL Reads
The cached path initializes the cache map lazily if needed, checking allocation size first and raising corruption if file size exceeds allocation. Normal cached reads use `CcCopyRead` or `CcCopyReadEx`; if the cache manager cannot wait and the IRP context is nonwaitable, the request is posted. MDL reads use `CcMdlRead` and require waitable processing.

## Directory And EA Reads
Directory and EA file reads are expected to be noncached paging I/O and sector-aligned. They are constrained to allocation size, return success with zero bytes when starting beyond allocation, and use `FatNonCachedIo`.

## Completion And Cleanup
The common finally path:
- Releases acquired FCB or paging resources.
- Posts requests through `FatFsdPostRequest` unless oplock handling already posted them.
- Updates synchronous file position for completed nonpaging reads.
- Marks `FO_FILE_FAST_IO_READ` on successful nonpaging reads so access time can be updated later.
- Frees stack `FAT_IO_CONTEXT` zero MDLs if the operation exits before normal async completion.
- Completes the IRP unless it was posted or already handed to async I/O.

## Important Notes
This is one of the central FastFAT data paths. Its critical invariants are EOF/VDL correctness, sector alignment for noncached I/O, resource choice between main and paging I/O resources, oplock and byte-range lock enforcement, and careful handling of low-stack conditions.
