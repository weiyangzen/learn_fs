# File Research: sources/windows/windows-driver-samples/filesys/fastfat/deviosup.c

Read fully: 3,801 lines.

This file implements FastFAT’s low-level device I/O support. It is the bridge between filesystem-level VBO operations and lower storage-stack LBO reads/writes, handling noncached I/O, paging-file I/O, multi-run request splitting, MDL setup, completion routines, device control requests, and disk accounting.

Core responsibilities:
- Translate file allocation runs from the FCB/DCB MCB into disk I/O runs.
- Dispatch single-run and multi-run read/write IRPs to `Vcb->TargetDeviceObject`.
- Manage synchronous versus asynchronous completions through `FAT_IO_CONTEXT`.
- Lock, map, and snapshot user buffers when FastFAT cannot rely on I/O manager direct-buffer setup.
- Support special paging-file I/O paths that cannot use the normal cached/noncached flow.
- Handle partial-sector noncached reads using an intermediate nonpaged buffer.
- Issue internal storage IOCTLs such as media-removal prevention.
- Build efficient zero MDLs for writing repeated zero pages.

Major routines:
- `FatPagingFileIo` maps paging-file VBOs through `Fcb->Mcb`, sends one IRP directly for a single contiguous run, or splits multi-run requests into associated IRPs and partial MDLs. It sets `SL_OVERRIDE_VERIFY_VOLUME` because paging I/O cannot tolerate normal verify processing. It uses a reserve MDL fallback and can reuse the master IRP synchronously when associated IRP allocation is constrained.
- `FatUpdateDiskStats` charges disk I/O to an originating process/thread on Windows 8+ builds, distinguishing reads and writes and avoiding double-accounting recursive/cache-manager activity.
- `FatNonCachedIo` is the main noncached read/write path. It locks the user buffer, optionally sets up a completion-time zeroing MDL for trailing bytes beyond `UserByteCount`, finds allocation runs, chooses a single-run fast path through `FatSingleAsync`, or builds an `IO_RUN` array and dispatches `FatMultipleAsync`.
- `FatNonCachedNonAlignedRead` handles non-sector-aligned reads by reading the leading and trailing sectors into a cache-aligned nonpaged buffer, copying only requested bytes to the user buffer, then delegating the aligned middle to `FatNonCachedIo`.
- `FatMultipleAsync` creates associated IRPs for each run, builds partial MDLs from the master MDL, installs sync or async multi-completion routines, handles write-through and override-verify flags, transfers async resource ownership when needed, and issues all lower-device IRPs.
- `FatSingleAsync` prepares the original IRP for a single contiguous lower-device request and installs either sync or async completion logic.
- `FatSingleNonAlignedSync` temporarily replaces the IRP MDL with an MDL over a nonpaged bounce buffer, sends a synchronous single-sector request, waits, then restores the original MDL.
- `FatWaitSync` waits on and clears the synchronous completion event in `IrpContext->FatIoContext`.
- Completion routines include `FatMultiSyncCompletionRoutine`, `FatMultiAsyncCompletionRoutine`, `FatSingleSyncCompletionRoutine`, `FatSingleAsyncCompletionRoutine`, `FatPagingFileCompletionRoutine`, and `FatPagingFileCompletionRoutineCatch`.
- `FatPagingFileErrorHandler` tries to mark the volume dirty with recovery requested after paging-file media errors, using a critical work item when possible.
- `FatLockUserBuffer`, `FatMapUserBuffer`, and `FatBufferUserBuffer` provide FastFAT’s explicit MDL/user-buffer handling.
- `FatToggleMediaEjectDisable` sends `IOCTL_DISK_MEDIA_REMOVAL` and tracks `VCB_STATE_FLAG_REMOVAL_PREVENTED`.
- `FatPerformDevIoCtrl` builds and waits for internal or external device-control IRPs, with optional verify override.
- `FatBuildZeroMdl` constructs an MDL that maps many pages to FastFAT’s single zero page, reducing memory needed for zero writes.

Important implementation details:
- The file treats allocation lookup failure for paging-file I/O as fatal corruption and bugchecks, because paging-file mappings are expected to be resident and valid.
- Multi-run paging I/O has careful master-IRP lifetime control: `AssociatedIrp.IrpCount` is manipulated so the master cannot complete before all child I/O is launched or drained.
- Async completion releases held resources, updates outstanding async-write counters, marks the master IRP pending, and frees the `FAT_IO_CONTEXT`.
- `STATUS_VERIFY_REQUIRED` is reposted only for suitable top-level async IRPs so volume verification can happen outside recursive completion context.
- `FatDoCompletionZero` zeroes a completion-time MDL only after successful I/O, then frees the MDL.
- Disk statistics are updated both for FastFAT per-volume counters and Windows process counter paths when enabled.
- The lower I/O dispatch macro currently maps directly to `IoCallDriver`, but keeps a named abstraction point for low-level read/write routing.

Research relevance:
This file is a compact study of Windows filesystem noncached I/O mechanics: MCB-to-LBO translation, associated IRPs, partial MDLs, paging-file constraints, completion-routine ownership, volume-verify handling, and storage-stack IOCTL issuance.
