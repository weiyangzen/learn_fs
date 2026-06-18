# File Research: sources/windows/reactos/ntoskrnl/mm/pagefile.c

## Purpose

`pagefile.c` implements ReactOS paging-file management and swap I/O. It validates and creates paging files, tracks paging-file slots with bitmaps, allocates/frees swap entries, reads and writes pages through MDL-based paging I/O, and exposes helper state for pagefile detection and out-of-swap reporting.

## Main Contents

- Defines minimum and architecture-specific maximum pagefile sizes.
- Maintains `MmPagingFile[MAX_PAGING_FILES]`, `MmPageFileCreationLock`, `MmNumberOfPagingFiles`, `MiFreeSwapPages`, `MiUsedSwapPages`, and reserved swap counters.
- Encodes swap entries with file index and page offset using `FILE_FROM_ENTRY`, `OFFSET_FROM_ENTRY`, and `ENTRY_FROM_FILE_OFFSET`.
- Builds one-page MDLs with `MmBuildMdlFromPages`.
- Detects paging files with `MmIsFileObjectAPagingFile`.
- Reports swap exhaustion once with `MmShowOutOfSpaceMessagePagingFile`.
- Performs swap I/O through `MmWriteToSwapPage`, `MmReadFromSwapPage`, and `MiReadPageFile`.
- Initializes globals in `MmInitPagingFile`.
- Allocates and frees swap slots with `MmAllocSwapPage` and `MmFreeSwapPage`.
- Implements the system call `NtCreatePagingFile`.

## Behavior And Data Flow

Swap entries reserve low bits for the paging-file index and store a one-based page offset. The first page of each pagefile is reserved as a header and never allocated. `MmAllocSwapPage` scans paging files for free space, marks one clear bitmap bit, updates global and per-file accounting, and returns an encoded entry. `MmFreeSwapPage` clears the corresponding bit and reverses the accounting.

`NtCreatePagingFile` validates caller privilege and user buffers, copies the name into paged pool, builds a DACL allowing SYSTEM and administrators, creates or opens the file with paging-file flags, validates size limits and device type, rejects floppy media, allocates the nonpaged `MMPAGING_FILE` descriptor and bitmap, initializes free-space accounting, inserts it into `MmPagingFile`, and initializes crash-dump support if the pagefile is on the boot partition.

## Concurrency And Invariants

- Pagefile list and slot accounting are guarded by `MmPageFileCreationLock`.
- Swap slot allocation assumes bitmap and free-space counters agree; unexpected bitmap failures bugcheck.
- Swap I/O validates that the target paging file and its device object exist before issuing paging I/O.
- User-mode creation requires `SeCreatePagefilePrivilege` and probes all user-supplied inputs.

## Notable Details

- Pagefile extension is recognized but not implemented; reopening an existing matching pagefile returns `STATUS_NOT_IMPLEMENTED` after validation.
- Several Windows-compatible validation steps are documented as TODOs, including section-object checks and notifying drivers to prepare for paging I/O.
- `MmZeroPageFile` and `MiReservedSwapPages` exist in this file but are not materially used by the shown logic.
- The device-type rejection path returns the current `Status` value rather than a newly assigned device-type-specific error, which is worth checking if this code is maintained.
