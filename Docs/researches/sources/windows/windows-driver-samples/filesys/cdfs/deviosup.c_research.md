# File Research: sources/windows/windows-driver-samples/filesys/cdfs/deviosup.c

Low-level CDFS device-I/O support for sector reads/writes, raw XA/audio reads, directory-sector caching, MDL handling, associated IRPs, and completion routines.

Key responsibilities:
- Defines `IO_RUN`, the internal description of disk extents, user buffers, transfer buffers, MDLs, and associated IRPs.
- Implements cooked noncached reads with `CdNonCachedRead`.
- Implements raw/XA/audio noncached reads with `CdNonCachedXARead`.
- Implements volume DASD writes with `CdVolumeDasdWrite`.
- Provides synchronous sector reads for mount/verify via `CdReadSectors`.
- Builds MDLs for user buffers with `CdCreateUserMdl`.
- Sends internal/external device controls with `CdPerformDevIoCtrlEx` and `CdPerformDevIoCtrl`.
- Prepares and finishes transfer buffers with `CdPrepareBuffers`, `CdPrepareXABuffers`, and `CdFinishBuffers`.
- Issues single and multiple lower-device I/O through `CdSingleAsync`, `CdMultipleAsync`, and `CdMultipleXAAsync`.
- Handles sync/async completion for single and associated IRPs.
- Implements a directory sector cache with `CdReadDirDataThroughCache` and `CdFreeDirCache`.
- Synthesizes pseudo path-table/root-directory data for audio disks with `CdReadAudioSystemFile`.
- Converts LBN to MSF with `CdLbnToMmSsFf`.
- Reuses an existing IRP to send a lower-device flush through `CdHijackIrpAndFlushDevice`.

Important behavior:
- Cooked reads operate in 2048-byte sectors and split work into up to `MAX_PARALLEL_IOS` runs.
- Unaligned cooked reads allocate nonpaged scratch buffers and copy the requested bytes back after the lower read completes.
- Async cooked reads are not allowed for unaligned or too-large multi-pass cases; those paths raise/post with `STATUS_CANT_WAIT`.
- XA/raw reads prepend synthetic RIFF/audio headers and translate raw 2352-byte sector offsets to cooked 2048-byte device offsets.
- XA raw reads are synchronous only and can retry Mode2 Form2 reads as Yellow Book Mode2 for known malformed media cases.
- `CdFinishBuffers` walks runs backward so shifting/copying within the user buffer does not overwrite later data.
- The VCB may cache one XA sector (`XASector`/`XADiskOffset`) to satisfy later partial raw-sector reads.
- Directory FCB reads can be satisfied through a chunked sector cache, with LRU replacement and synchronous lower reads into cache chunks.
- Audio disks get synthesized path-table and root-directory entries for tracks rather than ordinary ISO directory data.
- Async completion transfers resource ownership from the issuing thread to the I/O context so locks can be released safely after completion.

Dependencies:
- Depends on CDFS allocation lookup, VCB geometry/limits, TOC data, XA/audio constants, cache resources, I/O context allocation, FCB node types, target device object, and Windows IRP/MDL APIs.
- Uses `IoMakeAssociatedIrp`, partial MDLs, completion routines, `KeWaitForSingleObject`, `KeFlushIoBuffers`, `MmProbeAndLockPages`, and `MmBuildMdlForNonPagedPool`.

Notable risks:
- Buffer, MDL, and associated-IRP ownership is intricate; cleanup depends on `CleanupRunCount`, `SavedIrp`, `TransferMdl`, and whether the transfer buffer is the original user MDL or an allocated scratch page.
- Raw-sector math has separate raw/cooked offsets and 32-bit fast paths, making boundary correctness important.
- Directory-sector cache reads reuse a VCB-owned IRP and MDL and must always unlock/free MDLs and release cache resources.
- Async completion must release resources and free I/O contexts exactly once; resource-owner pointer handoff is subtle but required for thread lifetime safety.
