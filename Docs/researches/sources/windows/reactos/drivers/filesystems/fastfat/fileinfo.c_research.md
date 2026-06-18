# File Research: sources/windows/reactos/drivers/filesystems/fastfat/fileinfo.c

## Purpose

`fileinfo.c` implements FastFAT file-information query and set handling for ReactOS. It backs `IRP_MJ_QUERY_INFORMATION` and `IRP_MJ_SET_INFORMATION`, including metadata queries, timestamp and attribute updates, delete-on-close state, rename and replace semantics, current position updates, allocation changes, EOF changes, valid-data-length changes, EA owner-name repair during rename, and target deletion during replace-by-rename.

This is one of the central FastFAT metadata mutation files. It coordinates FCB/DCB/VCB locking, oplock breaks, cache manager state, memory-manager section checks, directory-entry updates, tunnel-cache behavior, FAT-specific short/LFN name generation, notifications, and best-effort rollback around non-transactional on-disk changes.

## Main Entry Points

- `FatFsdQueryInformation`
  - Dispatch wrapper for `IRP_MJ_QUERY_INFORMATION`.
  - Enters the filesystem, establishes top-level IRP state, creates an IRP context, calls `FatCommonQueryInformation`, and sends exceptions through FastFAT exception handling.

- `FatFsdSetInformation`
  - Dispatch wrapper for `IRP_MJ_SET_INFORMATION`.
  - Same top-level IRP and exception pattern as query, then calls `FatCommonSetInformation`.

- `FatCommonQueryInformation`
  - Decodes the file object and serves supported query classes.
  - Rejects user volume opens.
  - Acquires the VCB exclusively for name/all-information queries because full-name construction must synchronize with deletion/rename.
  - Acquires the FCB shared for normal files/directories except most paging-file cases, then verifies the FCB.
  - Writes result length through the IRP information field; negative remaining length is normalized to `STATUS_BUFFER_OVERFLOW`.

- `FatCommonSetInformation`
  - Decodes the file object and dispatches supported set classes.
  - Rejects user volume opens and root DCB mutation, except root delete returns `STATUS_CANNOT_DELETE`.
  - Performs oplock checks for file size/allocation/VDL changes and for rename/delete cases.
  - Acquires the VCB exclusively for rename and disposition operations to serialize with create and namespace changes.
  - Acquires the FCB exclusively for mutation unless paging-file deadlock rules apply.
  - Dispatches to the specific setter and unpins repinned BCBs before completion.

## Query Support

- `FatQueryBasicInfo`
  - Returns creation/access/write times and attributes.
  - Root directory reports synthetic January 1, 1980 timestamps converted through local/system time.
  - Adds `FILE_ATTRIBUTE_TEMPORARY` from FCB state and falls back to `FILE_ATTRIBUTE_NORMAL` when no attributes are set.

- `FatQueryStandardInfo`
  - Returns link count 1, delete-pending state, directory flag, allocation size, and EOF.
  - For normal files, lazily resolves allocation size if it is still the lookup hint.

- `FatQueryInternalInfo`
  - Returns the generated FAT file ID from the FCB.

- `FatQueryEaInfo`
  - Currently zeros `FILE_EA_INFORMATION`; the richer EA length lookup is disabled under `#if 0`.
  - Still keeps BCB cleanup structure for the disabled path.

- `FatQueryPositionInfo`
  - Returns `FileObject->CurrentByteOffset`.

- `FatQueryNameInfo`
  - Builds full path information from `Fcb->FullFileName`, synthesizing it if needed.
  - For non-normalized queries opened by short name, trims the final long-name component and appends the Unicode converted short name.
  - Handles partial copy with returned full available length and overflow status signaling.

- `FatQueryShortNameInfo`
  - Converts the stored OEM 8.3 short name to Unicode and returns it as `FILE_NAME_INFORMATION`.

- `FatQueryNetworkInfo`
  - Returns network-open metadata: times, attributes, allocation size, and EOF.
  - Mirrors basic/standard behavior for root timestamps, temporary attributes, normal fallback, and lazy allocation lookup.

## Set Support

- `FatSetBasicInfo`
  - Applies timestamps and FAT-supported attribute bits.
  - Treats `-1` timestamp inputs as "do not update this field later" and records that in CCB flags.
  - Converts NT times to FAT timestamps, with special handling for local-time values between December 31, 1979 and January 1, 1980.
  - Honors `FatData.ChicagoMode` for creation/access-time and long-name era behavior.
  - Rejects directory attributes on files and temporary attributes on directories.
  - Updates FCB state, dirent fields, dirty BCB state, and notify filters.
  - Rounds or truncates in-memory timestamps to FAT granularity.
  - Breaks parent directory oplocks on newer NT targets when access/write times or attributes change.

- `FatSetDispositionInfo`
  - Sets or clears delete-on-close.
  - Rejects deletion of read-only files, root directories, image-mapped files, and non-empty directories.
  - Checks write-protection by touching media: special floppy handling writes through a FAT byte; other media dirties the object dirent BCB.
  - Sets `FCB_STATE_DELETE_ON_CLOSE` and `FileObject->DeletePending`.
  - Notifies directory-change waiters when a directory becomes delete-pending.

- `FatSetRenameInfo`
  - Implements the full FAT rename/replace path.
  - Handles simple renames using the IRP buffer and fully qualified renames using a target directory file object.
  - Rejects root renames and cross-volume target directories.
  - For directory renames, walks the subtree to reject open descendants unless breakable batch oplocks can be broken, purges referenced file objects, and clears descendant cached full names.
  - Builds upcased Unicode names, OEM short-name candidates, tunnel-cache state, LFN requirements, and case-only rename detection.
  - In non-Chicago mode, requires 8.3-valid names and disables LFN/tunnel long-name use.
  - Locates target dirents, enforces `ReplaceIfExists`, rejects replacing directories/read-only files, and checks target FCB open/image-section state.
  - Allocates new dirent space when moving directories or changing required LFN dirent count.
  - Performs rename in phases: notify source removal/old-name, capture source dirent, tunnel source name, optionally delete source dirents, optionally delete replacement target, select final short/LFN names, write dirents, handle LFN sequences crossing page boundaries, update FCB dirent offsets and parent queue, update `..` for moved directories, rebuild FCB names, report final notifications, and rename EAs.
  - If an exception occurs during a sensitive on-disk/in-memory transition, marks the FCB bad rather than pretending rollback is complete.

- `FatSetPositionInfo`
  - Updates `FileObject->CurrentByteOffset`.
  - For noncached handles, enforces device alignment before accepting the new position.

- `FatSetAllocationInfo`
  - Changes allocation size for files only.
  - Rejects directories and invalid FAT I/O ranges.
  - Resolves lazy allocation size before mutation.
  - Initializes a cache map temporarily when a data section exists without a shared cache map.
  - Marks `FCB_STATE_TRUNCATE_ON_CLOSE` and the file object modified.
  - Extends allocation via `FatAddFileAllocation`; shrinks via `FatTruncateFileAllocation`.
  - When shrinking below file size, checks purge-failure mode and `MmCanFileBeTruncated`, serializes with paging I/O, adjusts file size/VDL/valid-data-to-disk, updates cache-manager sizes, writes dirent size, and reports size notification.
  - Restores in-memory file-size state on abnormal termination before the irreversible cache/dirent point.

- `FatSetEndOfFileInfo`
  - Changes EOF for files only.
  - Rejects directories and invalid ranges.
  - Supports `AdvanceOnly`, used for lazy file-size advancement into the dirent without reducing size.
  - Extends allocation when EOF exceeds allocation size.
  - On truncation, checks purge-failure mode and `MmCanFileBeTruncated`, then serializes with paging I/O.
  - Updates FCB file size, VDL, valid-data-to-disk, cache-manager sizes, dirent size, notification state, and truncate-on-close state.
  - On abnormal termination, restores in-memory sizes and attempts no-raise dirent rollback to avoid suspend/resume corruption cases.

- `FatSetValidDataLengthInfo`
  - Allows explicit VDL changes only for handles with manage-volume access.
  - Files only; VDL can only move forward and cannot exceed file size.
  - Requires `MmCanFileBeTruncated`.
  - Flushes and purges any existing data section before advancing VDL.
  - Updates FCB VDL, valid-data-to-disk, cache sizes, and modified state.

- `FatRenameEAs`
  - For non-FAT32 rename cases with EA metadata, opens the EA file, reads the EA set by old OEM name and EA index, updates the owner file name to the FCB’s new short name, marks the EA range dirty, and flushes the EA cache.
  - Catches FastFAT-handled exceptions and treats EA rename repair as best effort.

- `FatDeleteFile`
  - Used by rename-replace to remove an existing target file.
  - Removes matching cached FCB names from the prefix table, marks unopened cached target FCBs delete-on-close, zeroes size/VDL/cluster state under paging I/O synchronization, then creates a temporary FCB to truncate allocation and delete the dirent.

## Key Dependencies and Integration

- Depends on `fatprocs.h` for FastFAT structures, locking, exception, cache, allocation, dirent, EA, notify, tunnel, and name helpers.
- Uses I/O manager file objects, IRPs, current stack locations, share/file object flags, and delete-pending state.
- Uses FSRTL oplocks, notifications, tunnel cache, and name comparison/conversion helpers.
- Uses cache manager functions including `CcSetFileSizes`, `CcFlushCache`, `CcPurgeCacheSection`, cache-map initialization, and BCB pin/dirty/repin operations.
- Uses memory manager section checks including `MmFlushImageSection` and `MmCanFileBeTruncated`.
- Coordinates with create/cleanup/close behavior through FCB state flags such as delete-on-close, temporary, truncate-on-close, paging-file, and names-in-splay-tree.

## Important Invariants

- Namespace-changing operations acquire the VCB exclusively and reject recursion while create is in progress.
- Size-changing operations must coordinate with oplocks, paging I/O, MM truncation checks, cache-manager file sizes, and dirent updates.
- FAT is not transactional; some operations intentionally switch from reversible validation to irreversible mutation, then mark the FCB bad on exceptions.
- Delete-on-close is only set after delete feasibility has been checked.
- Rename of directories must ensure no open descendants remain, except requests that can be pended to break batch oplocks.
- Short-name versus long-name identity is tracked through CCB flags, FCB final-name length, tunnel-cache lookup, and prefix-table updates.
- Root DCB mutation is mostly forbidden.

## Notable Risks

- Rename is highly stateful and has many partial-failure windows involving old dirents, new dirents, target deletion, parent queues, cached names, and `..` updates.
- Allocation and EOF truncation depend on correct MM/cache purge behavior; stale mappings are explicitly treated as corruption risks.
- Some EA handling is best effort and can silently leave repair to later disk checking.
- Query buffer overflow is signaled indirectly by negative remaining length, so helper length accounting must stay exact.
- Time conversion depends on FAT granularity, local time, and special 1979/1980 compatibility behavior.
