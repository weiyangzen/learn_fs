# File Research: sources/windows/reactos/drivers/filesystems/fastfat/fatdata.c

## Purpose

`fatdata.c` defines global FastFAT driver state and implements shared control-path helpers: exception filtering, exception processing, request completion, top-level IRP tracking, Fast I/O information callbacks, and file-corruption popups.

## Global Data

The file defines:

- `FAT_DATA FatData`
- filesystem device objects:
  - `FatDiskFileSystemDeviceObject`
  - `FatCdromFileSystemDeviceObject`
- common `LARGE_INTEGER` constants:
  - zero/max
  - short delays
  - one day
  - Jan 1 1980 and Dec 31 1979
  - magic divisors for time conversion
- `FAT_TIME_STAMP FatTimeJanOne1980`
- `FAST_IO_DISPATCH FatFastIoDispatch`
- nonpaged lookaside lists:
  - IRP contexts
  - nonpaged FCBs
  - ERESOURCE objects
- close-context SLIST and close queue mutex
- reserve MDL/event for paging-file forward progress
- global disk accounting flag

Debug-only globals include trace level, counters, performance timing buckets, and breakpoint-trigger statuses.

## Exception Handling

`FatExceptionFilter`:

- Normalizes `STATUS_IN_PAGE_ERROR` to the embedded I/O status when present.
- If no IRP context exists, bugchecks on unexpected statuses and otherwise handles the exception.
- Marks the IRP context waitable.
- Disables write-through except for `STATUS_CANT_WAIT` and `STATUS_VERIFY_REQUIRED`.
- Stores expected exception status in `IrpContext->ExceptionStatus`.
- Bugchecks unexpected statuses.

`FatProcessException`:

- Handles the saved exception status after an FSD/FSP routine unwinds.
- Aborts MDL writes on write-complete-MDL failures.
- Unpins repinned BCBs with write-through disabled.
- Posts requests when the failure requires waiting or verify work cannot happen at the current APC/IRQL context.
- Completes recursive calls directly, translating cache-top-level verify-required into `STATUS_FILE_LOCK_CONFLICT`.
- Handles user-induced errors:
  - `STATUS_VERIFY_REQUIRED` routes to `FatPerformVerify`.
  - other user-induced errors can raise hard-error popups unless disabled.
- Marks volumes dirty or dirty-with-surface-test for corruption/media errors.
- Calls `FatMarkVolume` under exclusive VCB acquisition when appropriate.
- Completes the IRP through `FatCompleteRequest`.

## Request Completion

`FatCompleteRequest_Real`:

- Debug-breaks on configured interesting completion status.
- Ensures repinned BCBs are unpinned.
- Deletes the IRP context before completing the IRP.
- Clears `IoStatus.Information` on failed input operations to prevent copying invalid output.
- Sets final status and calls `IoCompleteRequest`.

`FatIsIrpTopLevel`:

- If no top-level IRP exists, installs the current IRP and returns true.
- Otherwise returns false.

## Fast I/O

`FatFastIoCheckIfPossible`:

- Accepts only `UserFileOpen`.
- Uses FsRtl byte-range lock checks.
- For writes, also rejects write-protected volumes.
- Does not acquire FCB resources; it is a quick feasibility check.

`FatFastQueryBasicInfo`:

- Accepts user file/directory opens.
- Acquires the FCB shared unless it is a paging file.
- Rejects bad FCB condition.
- Fills timestamps and attributes.
- Root DCB gets zero timestamps and directory attribute.
- Adds temporary/normal attributes as needed.

`FatFastQueryStdInfo`:

- Accepts user file/directory opens.
- Acquires the FCB shared unless paging file.
- Returns link count 1 and delete-pending state.
- For files, requires known allocation size; otherwise fails fast path.
- For directories, returns zero allocation/end-of-file and `Directory = TRUE`.

`FatFastQueryNetworkOpenInfo`:

- Similar acquisition and validation pattern.
- Supplies default change time based on Jan 1 1980.
- Handles root DCB specially.
- Fills allocation and EOF for files only when allocation size is known.

## User Notification

`FatPopUpFileCorrupt`:

- Suppresses popups for the root DCB.
- Ensures the FCB has a full filename.
- Avoids blocking system threads.
- Calls `IoRaiseInformationalHardError` with `STATUS_FILE_CORRUPT_ERROR`.

## Notable Details

- The file contains ReactOS-specific initializer variations for `LARGE_INTEGER` and thread pointer casts.
- Exception processing is tightly coupled to cache-manager state: repinned BCBs, MDL writes, verify handling, and volume dirtying all converge here.
- Fast I/O paths deliberately return false when state is incomplete, forcing the normal IRP path to handle slower or blocking cases.
