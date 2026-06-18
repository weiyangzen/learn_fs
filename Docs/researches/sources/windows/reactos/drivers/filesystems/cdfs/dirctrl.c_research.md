# File Research: sources/windows/reactos/drivers/filesystems/cdfs/dirctrl.c

## Purpose
Implements CDFS directory-control handling: directory enumeration, directory-change notification registration, enumeration-state initialization, wildcard/version matching, short-name matching, and formatting directory entries into Windows query-directory information classes.

## Key Elements
- `CdCommonDirControl` decodes the file object, accepts only `UserDirectoryOpen`, and dispatches `IRP_MN_QUERY_DIRECTORY` to `CdQueryDirectory` or `IRP_MN_NOTIFY_CHANGE_DIRECTORY` to `CdNotifyChangeDirectory`.
- `CdQueryDirectory` validates supported information classes, maps the caller buffer, initializes a `FILE_ENUM_CONTEXT`, acquires/verifies the directory FCB, initializes enumeration state, loops over matching dirents, formats result records, handles buffer overflow/partial-name rules, updates CCB restart state, releases resources, sets `IoStatus.Information`, and completes the IRP.
- Supported result classes are `FileDirectoryInformation`, `FileFullDirectoryInformation`, `FileIdFullDirectoryInformation`, `FileNamesInformation`, `FileBothDirectoryInformation`, and `FileIdBothDirectoryInformation`.
- Result formatting fills timestamps from the CD dirent time, sets directory versus read-only file attributes, propagates hidden attributes, reports file sizes/allocation sizes for files, writes CDFS dirent offsets as file indexes, emits file IDs for ID-bearing classes, and includes short names for both-directory classes when applicable.
- Version-string output is conditional: the semicolon and version are returned when the search expression includes a version or when a directory has an illegal version-like component.
- `CdNotifyChangeDirectory` supports notify requests even though read-only CD-ROM media will not generate ordinary changes; it verifies the VCB and queues the IRP with `FsRtlNotifyFullChangeDirectory`, then completes only the CDFS IRP context and returns pending.
- `CdInitializeEnumeration` resets or initializes CCB search state, converts the caller's query pattern to a `CD_NAME`, detects wildcard use in name/version components, upcases case-insensitive expressions, treats missing/empty/single-star as match-all, suppresses root `"."` and `".."` constant entries, chooses the starting dirent from restart/index/CCB state, ensures the directory stream file exists, positions the file context, and returns flags controlling current versus next entry and single-entry behavior.
- `CdEnumerateIndex` walks dirents from the current position, skips constant root entries when requested, ignores associated files, suppresses duplicate version entries when the search has no version component, matches long names first, generates/checks 8.3 short names when needed, and expands a found file to its last dirent before returning.

## Dependencies
Depends on CDFS directory stream creation and dirent traversal helpers, name conversion/upcasing/wildcard matching, 8.3 name generation, file-ID packing, time conversion, user-buffer mapping, FsRtl directory-notification support, FCB/CCB locking, and the CDFS `FILE_ENUM_CONTEXT` lifetime helpers.

## Behavior/Risks
- Query-directory follows Windows buffer semantics: the first entry may be partially returned with `STATUS_BUFFER_OVERFLOW`, while later entries that do not fit are not copied and enumeration resumes from that entry on a later call.
- CCB enumeration state is updated only after successful or non-error progress, recording both current dirent offset and whether the next query should return the current or next entry.
- Search expressions are stored in the CCB and reused until restart with a new pattern; restart-scan handling frees the prior allocated expression unless it was the match-all sentinel.
- Root enumeration intentionally hides constant self/parent entries for consistency with Microsoft filesystem behavior.
- Version handling affects both matching and duplicate suppression; without an explicit version search, only the first version sequence entry is returned.
- User-buffer writes are exception guarded because these requests are not necessarily buffered by the I/O manager.
- Notify requests always pend through FsRtl and depend on cleanup/cancel paths elsewhere to remove queued notifications.
