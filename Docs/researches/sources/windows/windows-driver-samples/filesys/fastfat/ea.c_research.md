# File Research: sources/windows/windows-driver-samples/filesys/fastfat/ea.c

## Scope And Role

`ea.c` is the FastFat extended-attribute dispatch file. In this sample version, the live EA query and set common routines deliberately complete with `STATUS_INVALID_DEVICE_REQUEST`; most historical FAT EA implementation logic is retained under `#if 0`.

The file is in subset A through `sources/windows/windows-driver-samples`, and was read completely.

## Live Entry Points

- `FatFsdQueryEa`: FSD dispatch wrapper for `IRP_MJ_QUERY_EA`.
- `FatFsdSetEa`: FSD dispatch wrapper for `IRP_MJ_SET_EA`.
- `FatCommonQueryEa`: live implementation completes the IRP with `STATUS_INVALID_DEVICE_REQUEST` and returns that status.
- `FatCommonSetEa`: live implementation completes the IRP with `STATUS_INVALID_DEVICE_REQUEST` and returns that status.

The dispatch wrappers enter the filesystem with `FsRtlEnterFileSystem`, establish top-level IRP state with `FatIsIrpTopLevel`, create an IRP context using waitability from `CanFsdWait`, call the common routine, process FastFat exceptions, clear top-level IRP state when appropriate, and exit the filesystem.

## Disabled Historical Query Path

The disabled `FatCommonQueryEa` block shows the intended full algorithm:

1. Decode the file object and allow only user file/directory opens, excluding the root DCB.
2. Reject FAT32 with `STATUS_EAS_NOT_SUPPORTED`.
3. Acquire the FCB shared, map the user buffer, verify the FCB, and read the file’s dirent.
4. Check EA modification count consistency against the CCB for resumable enumeration.
5. If the dirent EA handle is zero, treat the file as having no EAs.
6. Otherwise get the volume EA file, validate that an EA database exists, read the EA set, and derive packed-EA range and length.
7. Clear the user output buffer and choose one of three helper paths: user EA-name list, index-specified scan, or simple scan.
8. Release FCBs, unpin BCBs and EA ranges, then complete the IRP.

## Disabled Historical Set Path

The disabled `FatCommonSetEa` block shows a wholesale replacement model:

1. Decode the file object, reject invalid opens/root DCB and FAT32.
2. Buffer and validate the caller’s full-EA list with `IoCheckEaBufferValidity`.
3. Require a waitable context, set `FO_FILE_MODIFIED`, and acquire VCB/FCB resources; write-through mode also acquires parent/root DCBs to preserve lock order.
4. Read the existing EA handle from the object dirent.
5. If previous EAs exist, read the EA file and current EA set.
6. Allocate a cluster-rounded EA set buffer, copy previous packed EAs or initialize a new owner-name header.
7. For each input `FILE_FULL_EA_INFORMATION`, validate name/flags, delete any existing packed EA with the same name, and append non-empty replacements.
8. If packed EAs remain, allocate a new EA set in the EA file, copy header/list data, dirty and flush the EA range.
9. Delete the previous EA set if one existed.
10. Store the new EA handle in the object dirent, dirty the dirent, notify `FILE_NOTIFY_CHANGE_EA`, and release all resources.

## Disabled Helper Routines

All helper implementations are inside `#if 0`:

- `FatQueryEaUserEaList`: handles explicit EA-name lists, validates names, skips duplicate requested names, returns dummy empty EAs for missing names, copies found packed EAs to full-EA records, and reports overflow status.
- `FatQueryEaIndexSpecified`: converts a 1-based EA index into an offset and delegates to simple scan, distinguishing nonexistent entries from end-of-list.
- `FatQueryEaSimpleScan`: copies packed EAs into caller full-EA records from a starting offset, updating `Ccb->OffsetOfNextEaToReturn`.
- `FatIsDuplicateEaName`: scans previous request entries and compares upcased EA names.

Because the entire block is disabled, these helpers are not compiled despite their prototypes.

## Integration Points

The live code integrates only with dispatch, IRP-context, top-level IRP, exception, and request-completion helpers. The disabled code references broader FastFat EA infrastructure such as `FatGetEaFile`, `FatReadEaSet`, `FatAddEaSet`, `FatDeleteEaSet`, packed EA manipulation helpers, EA range pinning/dirtying, and CCB EA enumeration state.

## Risks And Test Signals

The effective behavior is simple: EA query/set should return `STATUS_INVALID_DEVICE_REQUEST`. Regression tests should assert both FSD wrappers complete that way and preserve normal FastFat exception/top-level IRP cleanup behavior. If the disabled EA implementation were ever re-enabled, the high-risk areas would be user-buffer probing, packed/full EA size alignment, resumable enumeration offsets, EA database corruption handling, lock ordering across VCB/FCB/root/parent/EA FCB, and consistency between dirent EA handles and EA file contents.
