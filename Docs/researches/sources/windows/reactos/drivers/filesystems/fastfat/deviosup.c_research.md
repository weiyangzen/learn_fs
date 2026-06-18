# File Research: sources/windows/reactos/drivers/filesystems/fastfat/deviosup.c

## Purpose

`deviosup.c` is the low-level device I/O support layer for ReactOS fastfat. It translates FAT file byte ranges into disk logical byte offsets, builds IRPs/associated IRPs and MDLs, sends read/write requests to the lower storage stack, waits or completes asynchronously, and handles user-buffer locking/mapping plus internal device-control requests.

The file sits below read/write dispatch logic and above the target disk device. Its central responsibility is preserving Windows fastfat semantics around paging I/O, noncached I/O, synchronous versus asynchronous completion, verify handling, dirty-volume escalation on paging-file media errors, and completion-time buffer zeroing.

## Main Entry Points

- `FatPagingFileIo` handles paging-file I/O without ordinary completion processing. It maps VBO runs through the file Mcb, sends a single IRP directly when possible, otherwise splits across runs using associated IRPs or the master IRP with a reserve MDL fallback.
- `FatNonCachedIo` is the general noncached read/write path. It locks the caller buffer, optionally prepares completion-time zeroing for unreadable trailing bytes, maps the file allocation with `FatLookupFileAllocation`, and dispatches either `FatSingleAsync` or `FatMultipleAsync`.
- `FatNonCachedNonAlignedRead` handles non-sector-aligned noncached reads by using a one-sector cache-aligned pool buffer for unaligned head/tail sectors and delegating aligned middle ranges back to `FatNonCachedIo`.
- `FatMultipleAsync` builds associated IRPs, partial MDLs, stack locations, completion routines, and accounting for multiple noncontiguous disk runs.
- `FatSingleAsync` reuses the caller IRP for a single contiguous disk run.
- `FatSingleNonAlignedSync` temporarily replaces the IRP MDL with an MDL over a nonpaged staging buffer for synchronous sector reads.
- `FatWaitSync` waits on the `FatIoContext` sync event set by completion routines.
- `FatLockUserBuffer`, `FatMapUserBuffer`, and `FatBufferUserBuffer` provide FAT’s explicit user-buffer management because the filesystem does not rely on direct I/O setup from the I/O manager.
- `FatToggleMediaEjectDisable` and `FatPerformDevIoCtrl` build and submit internal device-control IRPs.
- `FatBuildZeroMdl` creates an MDL that represents a repeated zero page for efficient zero writes or zero-fill style operations.

## I/O Flow

The common pattern is: caller prepares a `FAT_IO_CONTEXT`, this file locks/maps the buffer, converts VBO to LBO, chooses single or multiple request dispatch, installs a completion routine, sends to `Vcb->TargetDeviceObject`, then either waits or returns pending.

`FatNonCachedIo` first validates that file allocation exists. Missing allocation after the upper layer expected allocation is treated as corruption via `FatPopUpFileCorrupt` and `STATUS_FILE_CORRUPT_ERROR`. For single runs it increments noncached stats and calls `FatSingleAsync`. For multiple runs it builds an `IO_RUN` array, initializes the master IRP status to success/full byte count, then calls `FatMultipleAsync`.

`FatMultipleAsync` does all fallible allocation before issuing any driver requests. If associated IRP/MDL allocation fails, it unwinds only the IRPs built so far. Once it starts calling the lower driver, an unexpected raise is considered unrecoverable and bugchecks.

Paging-file I/O has a stricter path. `FatPagingFileIo` asserts `FCB_STATE_PAGING_FILE`, requires the Mcb lookup to succeed, bypasses volume verify with `SL_OVERRIDE_VERIFY_VOLUME`, and avoids normal completion ownership. For fragmented paging files it creates associated IRPs per run when possible, but can reuse the master IRP synchronously when associated IRP allocation or MDL allocation pressure forces use of `FatReserveMdl`.

## Completion Behavior

The completion routines divide into synchronous, asynchronous, paging-file, and special APC-level variants.

- `FatMultiSyncCompletionRoutine` copies error status to the master IRP, frees associated IRP MDL/IRP, decrements `Context->IrpCount`, performs any completion zeroing when the last run finishes, and signals the sync event.
- `FatMultiAsyncCompletionRoutine` also consolidates errors into the master IRP. On final completion it sets requested byte count on success, marks fast-read or modified flags for nonpaging I/O, decrements outstanding async write counters, releases captured resources, marks the master IRP pending, frees the context, and may repost `STATUS_VERIFY_REQUIRED` top-level requests.
- `FatSingleSyncCompletionRoutine` performs completion zeroing and signals the sync event.
- `FatSingleAsyncCompletionRoutine` mirrors the async multi-run finalization path for single-run I/O.
- `FatPagingFileCompletionRoutine` is invoked on paging-file error/cancel and copies error status to the master IRP if needed.
- `FatPagingFileCompletionRoutineCatch` handles the synchronous master-IRP reuse case, frees or returns the reserve MDL, restores the original MDL, and either signals the waiter or lets dirty-volume recovery work complete it.
- `FatSpecialSyncCompletionRoutine` is used for APC-level-compatible internal IRPs such as media-removal toggles; it copies status into a local sync context and signals without holding the caller to ordinary final IRP completion timing.

`FatDoCompletionZero` is a key helper macro: if `Context->ZeroMdl` is set and the I/O succeeded, it zeroes the mapped tail bytes and frees the MDL. This supports sector-aligned physical reads where only part of the final bytes are user-visible.

## State, Dependencies, and Side Effects

This file depends heavily on kernel I/O primitives (`IoCallDriver`, `IoMakeAssociatedIrp`, MDLs, IRP stack locations), cache/FSRTL helpers, FAT Mcb allocation lookup, `FAT_IO_CONTEXT`, VCB statistics, and global fastfat data such as `FatData`, `FatReserveMdl`, `FatReserveEvent`, `FatDiskAccountingEnabled`, and debug flags.

It updates per-processor filesystem statistics, optional Windows 8+ disk accounting counters, file-object flags (`FO_FILE_FAST_IO_READ`, `FO_FILE_MODIFIED`), outstanding async write counters/events, removable-media prevention state in `Vcb->VcbState`, and dirty-volume recovery state through queued work items on paging-file media errors.

## Correctness Notes and Risks

The highest-risk areas are MDL/IRP lifetime and completion ownership. Multi-run dispatch depends on exact associated IRP counts and on not allowing the I/O manager to complete the master IRP before FAT has reconciled state. The paging-file path is especially sensitive because it tries to continue under low-memory pressure using a global reserve MDL and may synchronously reuse the master IRP.

`STATUS_VERIFY_REQUIRED` handling is intentionally limited: only top-level nonrecursive async I/O is reposted because recursive I/O cannot safely perform volume verification. Paging-file I/O overrides verify entirely.

Media-error handling for paging files is best effort. `FatPagingFileErrorHandler` queues dirty/recover marking for non-total-device failures, but comments explicitly note no full forward-progress guarantee.

The file includes conditional Windows-version and `__REACTOS__` sections around disk accounting; those paths should be checked carefully when changing compile-time feature levels because some accounting variables are only declared outside ReactOS builds while accounting macros may compile away depending on `NTDDI_VERSION`.

## Research Coverage

Read completely. Covered declarations, paging-file I/O, noncached aligned and nonaligned paths, single/multiple dispatch, all completion routines, user-buffer helpers, media-removal/device-control helpers, and zero-MDL construction.
