# File Research: sources/windows/reactos/drivers/filesystems/fastfat/ea.c

## Purpose

`ea.c` implements the dispatch-facing Extended Attribute operations for FastFAT: `IRP_MJ_QUERY_EA` and `IRP_MJ_SET_EA`. In this ReactOS source snapshot, the real query/set implementations are compiled out with `#if 0`; the active common routines immediately complete requests with `STATUS_INVALID_DEVICE_REQUEST`.

## Active Runtime Behavior

- `FatFsdQueryEa(...)`
  - Enters filesystem context.
  - Marks top-level IRP if applicable.
  - Creates an IRP context.
  - Calls `FatCommonQueryEa`.
  - Uses `FatExceptionFilter` and `FatProcessException` for structured exception handling.
- `FatFsdSetEa(...)`
  - Same dispatch pattern as query.
  - Calls `FatCommonSetEa`.
- `FatCommonQueryEa(...)`
  - Active code calls `FatCompleteRequest(..., STATUS_INVALID_DEVICE_REQUEST)`.
  - Returns `STATUS_INVALID_DEVICE_REQUEST`.
- `FatCommonSetEa(...)`
  - Active code calls `FatCompleteRequest(..., STATUS_INVALID_DEVICE_REQUEST)`.
  - Returns `STATUS_INVALID_DEVICE_REQUEST`.

So although the FSD entry points exist, EA query/set are effectively unsupported at this layer in the compiled code.

## Disabled Query Implementation

The disabled `FatCommonQueryEa` body documents the intended design:

- Accepts only `UserFileOpen` and `UserDirectoryOpen`; rejects root DCB.
- Rejects FAT32 with `STATUS_EAS_NOT_SUPPORTED`.
- Requires a waitable context or posts the request.
- Acquires the target FCB shared.
- Reads the file dirent to obtain `Dirent->ExtendedAttributes`, the EA handle.
- If handle is zero, returns from an empty EA set.
- Otherwise opens/locks the EA data file using `FatGetEaFile`, reads the EA set through `FatReadEaSet`, and exposes packed EAs as full EA records.
- Supports three query modes:
  - user-supplied EA name list via `FatQueryEaUserEaList`
  - index-specified scan via `FatQueryEaIndexSpecified`
  - sequential scan via `FatQueryEaSimpleScan`
- Tracks resume state with `Ccb->OffsetOfNextEaToReturn`.
- Uses `Fcb->EaModificationCount` and `Ccb->EaModificationCount` to detect changes during enumeration.

## Disabled Set Implementation

The disabled `FatCommonSetEa` body documents replacement-style EA updates:

- Validates open type and rejects FAT32.
- Buffers and validates user EA input with `IoCheckEaBufferValidity`.
- Requires waitable context.
- Acquires VCB/FCB and, for write-through, parent/root DCBs in a prescribed order.
- Reads existing packed EA data if present.
- For each full EA:
  - validates EA name with `FatIsEaNameValid`
  - rejects unsupported flags
  - deletes any existing same-name packed EA
  - appends a new packed EA if the value length is nonzero
- Adds a new EA set with `FatAddEaSet` if packed EAs remain.
- Deletes the previous EA set with `FatDeleteEaSet`.
- Updates the owning dirent’s `ExtendedAttributes` handle.
- Marks the dirent dirty and emits `FILE_NOTIFY_CHANGE_EA`.

## Disabled Helper Algorithms

- `FatQueryEaUserEaList`
  - Validates requested EA names.
  - Skips duplicate names.
  - Returns matching packed EA data or a dummy zero-value EA record.
  - Uppercases returned dummy names.
  - Handles overflow vs success carefully.
- `FatQueryEaIndexSpecified`
  - Converts a 1-based EA index into a packed-EA offset.
  - Distinguishes nonexistent entry from no-more-EAs.
  - Delegates output construction to `FatQueryEaSimpleScan`.
- `FatQueryEaSimpleScan`
  - Iterates packed EAs from a start offset.
  - Copies packed EA data into `FILE_FULL_EA_INFORMATION` records.
  - Maintains next-entry offsets and CCB resume offset.
  - Returns `STATUS_NO_EAS_ON_FILE`, `STATUS_NO_MORE_EAS`, `STATUS_BUFFER_TOO_SMALL`, `STATUS_BUFFER_OVERFLOW`, or success as appropriate.
- `FatIsDuplicateEaName`
  - Searches only earlier entries in the caller’s EA-name list.
  - Compares names case-insensitively after upcasing.

## Integration

The active file depends on exception/completion support from `fatdata.c`. The disabled implementation depends heavily on lower-level EA file machinery from `easup.c` and EA on-disk structures/macros from `fat.h`.
