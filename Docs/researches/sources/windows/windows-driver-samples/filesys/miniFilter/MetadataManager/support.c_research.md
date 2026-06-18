# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/support.c

## Purpose

`support.c` implements small support routines for the MetadataManager minifilter sample.

It provides:

- Unicode string allocation/free helpers.
- Volume-open detection.
- Implicit volume-lock detection.

These helpers are used by `DataStore.c` and `operations.c`.

## `FmmAllocateUnicodeString`

Allocates a paged-pool Unicode buffer using `ExAllocatePoolZero`.

Inputs and behavior:

- The caller sets `String->MaximumLength`.
- The function allocates that many bytes with `FMM_STRING_TAG`.
- On success:
  - `String->Buffer` is set.
  - `String->Length` is reset to zero.
  - Returns `STATUS_SUCCESS`.
- On allocation failure:
  - Logs a debug error.
  - Returns `STATUS_INSUFFICIENT_RESOURCES`.

This helper is used while constructing full metadata filenames.

## `FmmFreeUnicodeString`

Frees a Unicode string allocated by `FmmAllocateUnicodeString`.

Behavior:

- Calls `ExFreePoolWithTag` with `FMM_STRING_TAG`.
- Resets `Length`, `MaximumLength`, and `Buffer`.

The routine assumes the buffer is non-null and owned by this helper.

## `FmmTargetIsVolumeOpen`

Determines whether the callback target is a volume file object.

Behavior:

- Returns true when:
  - `Cbd->Iopb->TargetFileObject` is non-null, and
  - the target file object has `FO_VOLUME_OPEN`.
- Returns false otherwise.

This is used throughout operation callbacks to restrict metadata release/reacquire logic to volume opens.

## `FmmIsImplicitVolumeLock`

Determines whether a create/open on a volume implies a volume lock.

Behavior:

1. Gets the instance context from `Cbd->Iopb->TargetInstance`.
2. Reads `Cbd->Iopb->Parameters.Create.ShareAccess`.
3. Switches on the attached filesystem type.
4. For ReFS, NTFS, and FAT:
   - Treats the open as an implicit volume lock when the caller does not allow `FILE_SHARE_WRITE` or `FILE_SHARE_DELETE`.
5. For other filesystems:
   - Returns `STATUS_INVALID_PARAMETER`.
6. Releases the instance context before returning.

The operation is considered an implicit lock because denying write/delete sharing requires other writable/deletable handles on the volume to be absent, so the filter must close its own metadata file to let the open succeed.

## Supported Filesystems

The implicit-lock logic recognizes:

- `FLT_FSTYPE_REFS`
- `FLT_FSTYPE_NTFS`
- `FLT_FSTYPE_FAT`

This matches the attach policy in `FmmInstanceSetup`.

## Research Notes

`support.c` is small but important to callback correctness. `FmmTargetIsVolumeOpen` prevents ordinary file opens from triggering volume metadata release logic, and `FmmIsImplicitVolumeLock` lets the sample cooperate with tools that lock a volume by opening it with restrictive sharing rather than by issuing an explicit FSCTL.
