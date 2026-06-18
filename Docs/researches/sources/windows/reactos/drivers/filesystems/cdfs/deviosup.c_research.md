# File Research: sources/windows/reactos/drivers/filesystems/cdfs/deviosup.c

## Purpose
Provides the low-level disk I/O support used by CDFS for noncached cooked-sector reads, XA/raw-sector reads, volume DASD writes, mount/verify reads, internal device controls, directory-sector caching, async associated-IRP fanout, synchronous waits, completion routines, pseudo audio-directory generation, and IRP-based device flushing.

## Key Elements
- Defines `IO_RUN`, the per-run descriptor used to map a logical file read into disk offset/count, user buffer position, transfer buffer/MDL, and optional associated IRP. `MAX_PARALLEL_IOS` limits fanout to five runs.
- `CdLbnToMmSsFf` converts logical block numbers to CD MSF format with the standard 150-frame bias.
- `CdFileTrackMode` maps XA/audio FCB state flags to raw-read `TRACK_MODE_TYPE` values.
- `CdNonCachedRead` locks/maps the user buffer, handles synthetic audio root/path-table reads, enables waitable operation for directory sector-cache use, prepares cooked-sector `IO_RUN`s, chooses single versus multiple async I/O, waits for synchronous requests, copies unaligned reads back, flushes I/O buffers when needed, and cleans partial allocations on exit.
- `CdNonCachedXARead` reads raw 2352-byte sectors for XA/audio files, synthesizes a leading RIFF/audio header, limits reads to file size, prepares raw-sector runs, issues `IOCTL_CDROM_RAW_READ`, retries suspicious Mode2 Form2 failures as Yellow Book Mode2, saves the final raw sector for reuse, and always flushes I/O buffers after synchronous raw reads.
- `CdVolumeDasdWrite` locks the caller buffer for read access and forwards a single direct write/read-major operation to the lower device through `CdSingleAsync`.
- `CdReadSectors` builds a synchronous read IRP for mount/verify paths, sets `SL_OVERRIDE_VERIFY_VOLUME`, waits on pending completion, and either returns a boolean error indication or raises normalized status.
- `CdCreateUserMdl` allocates and probes/locks an MDL for user buffers because CDFS does not rely on the I/O manager's direct-I/O buffer locking here.
- `CdPerformDevIoCtrlEx` and `CdPerformDevIoCtrl` build synchronous device-control IRPs, optionally use internal-device-control semantics, optionally override verify, wait for completion, and return the lower-driver status plus optional IOSB data.
- `CdPrepareBuffers` maps cooked logical reads to disk allocation runs and allocates page-sized nonpaged scratch buffers for unaligned sector starts or sub-sector tails that cannot be issued directly.
- `CdPrepareXABuffers` maps raw-file offsets past the RIFF header to cooked disk sectors, reuses `Vcb->XASector` on matching disk offsets, chooses direct user-buffer raw-sector transfers when possible, respects raw-transfer and physical-page limits, and allocates scratch buffers for partial raw sectors.
- `CdFinishBuffers` walks runs backward, copies scratch-buffer data to the user buffer when not doing final cleanup, frees MDLs/IRPs/buffers, and can save one XA transfer buffer in the VCB for later partial-sector reuse.
- `CdReadDirDataThroughCache`, `CdFreeDirCache`, and `CdSyncCompletionRoutine` implement a shared/exclusive directory-sector cache that reads aligned chunks into VCB cache slots, tracks LRU replacement, handles TOC-based end-of-disc clipping, and has a ReactOS fallback when `CdromToc` is absent.
- `CdMultipleAsync` builds associated read IRPs for multiple cooked runs or services directory runs through the sector cache, sets master-IRP and CDFS I/O-context counts, adjusts resource ownership for true async completion, and issues all lower-device requests after allocation succeeds.
- `CdMultipleXAAsync` builds associated IRPs for raw-sector IOCTL reads, including partial MDLs sized for raw bytes and stack locations populated with `RAW_READ_INFO`.
- `CdSingleAsync` handles a single run directly on the original IRP, optionally using the directory-sector cache, installs sync or async completion, adjusts resource ownership for async requests, and sends the read/write to the lower driver.
- `CdWaitSync` waits on and clears the CDFS I/O-context sync event.
- Completion routines update aggregate status and information, free associated IRPs/MDLs where CDFS owns them, signal synchronous waiters, mark async master IRPs pending, release resources for async completion, and free I/O contexts.
- `CdReadAudioSystemFile` synthesizes the path table and root directory content for audio disks, including self/parent entries and per-track pseudo entries with XA system-use data.
- `CdHijackIrpAndFlushDevice` reuses an existing IRP stack location as `IRP_MJ_FLUSH_BUFFERS`, waits through `CdSyncCompletionRoutine`, treats unsupported flush as success, and restores visible IRP status fields.

## Dependencies
Depends on CDFS allocation lookup, VCB/FCB state, XA/audio constants, directory cache resources, I/O-context allocation, MDL helpers, Windows IRP construction/completion APIs, CD-ROM raw-read structures, TOC data, sector-size conversion macros, and memory-pool tags from the CDFS codebase.

## Behavior/Risks
- Cooked reads operate in 2048-byte logical sectors, while XA reads expose raw 2352-byte sectors with a synthetic RIFF-style header, so buffer sizing and offset conversion are intentionally different between paths.
- Asynchronous cooked reads are allowed only when the request can be described safely; unaligned transfers require waitable synchronous processing because scratch buffers must be copied and flushed before completion.
- The directory-sector cache changes the normal lower-driver I/O path for directory FCBs and can force nonwaitable requests into waitable mode before read preparation.
- XA partial-sector caching stores one raw sector globally in the VCB, protected by the VCB lock; later reads may avoid a lower-device raw read when the disk offset matches.
- The Mode2 Form2 fallback mutates FCB state to remember that the file should be treated as Yellow Book Mode2 after a successful retry.
- Many paths raise status on allocation/probing/read failures rather than returning ordinary error codes, so callers rely on structured cleanup in surrounding CDFS dispatch code.
- Associated-IRP completion is delicate: synchronous multi-I/O completions return `STATUS_MORE_PROCESSING_REQUIRED` and free IRPs themselves, while async completion lets the final associated IRP complete the master path after updating status and releasing resources.
- The ReactOS fallback in the directory cache when `CdromToc` is missing explicitly risks reading past partition end, as noted by the in-source comment.
