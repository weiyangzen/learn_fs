# File Research: sources/windows/reactos/drivers/filesystems/udfs/dircntrl.cpp

## Purpose

`dircntrl.cpp` implements UDFS directory-control handling for `IRP_MN_QUERY_DIRECTORY` and `IRP_MN_NOTIFY_CHANGE_DIRECTORY`. It formats directory entries into NT query-directory information classes, maintains per-CCB enumeration state, supports wildcard/case-insensitive matching, and queues directory change notifications.

## Main Entry Points

- `UDFDirControl(PDEVICE_OBJECT, PIRP)`: top-level `IRP_MJ_DIRECTORY_CONTROL` dispatch wrapper. It creates an IRP context, calls `UDFCommonDirControl`, handles exceptions, and restores top-level IRP state.
- `UDFCommonDirControl(PtrUDFIrpContext, PIRP)`: validates file-object context, acquires the VCB shared, and dispatches to query-directory or notify-change handling by minor function.
- `UDFQueryDirectory(...)`: implements directory enumeration and output-buffer formatting.
- `UDFFindNextMatch(...)`: scans a UDF directory index for the next undeleted, non-internal entry matching a pattern/hash.
- `UDFNotifyChangeDirectory(...)`: queues or completes directory-change notification requests using FsRtl notify support.

## Query Directory Flow

`UDFQueryDirectory` validates that the target FCB is a directory and not a VCB, determines whether it can block, and posts the request if not. It derives the VCB, NT-required FCB, CCB, directory `UDF_FILE_INFO`, requested buffer length, requested information class, and caller search flags.

Supported information classes are:

- `FileDirectoryInformation`
- `FileFullDirectoryInformation`
- `FileNamesInformation`
- `FileBothDirectoryInformation`

The routine computes the fixed base length for the requested class, acquires the FCB main resource shared, maps either the MDL or user buffer, normalizes a trailing NUL in the search pattern, and chooses the active enumeration pattern.

## Search Pattern and Enumeration State

Each directory handle stores search state in its CCB:

- `DirectorySearchPattern` stores the first or overridden non-match-all pattern.
- `CurrentIndex` stores the last returned directory index.
- `UDF_CCB_MATCH_ALL`, `UDF_CCB_WILDCARD_PRESENT`, and `UDF_CCB_CAN_BE_8_DOT_3` describe how matching should work.
- `hashes` caches UDF name hashes for non-wildcard patterns.

The code supports:

- `SL_INDEX_SPECIFIED`: start from `FileIndex + 1`, ignore the pattern, and match all.
- `SL_RESTART_SCAN`: restart at index 0.
- Continued scans: start at `Ccb->CurrentIndex + 1`.
- Case-insensitive opens: upcase the supplied pattern and set the ignore-case flag unless the CCB marks a case-sensitive open.

## Directory Matching

`UDFFindNextMatch` iterates through `UDFDirIndex(hDirIndex, EntryNumber)`, skips entries without names, deleted entries, and internal file-info entries, optionally prefilters by long/POSIX/DOS hash, then calls `UDFIsNameInExpression`. Matching flags indicate whether the pattern can be 8.3, whether matching ignores case, and whether it contains wildcards. Entries 0 and 1 are treated specially through the final `EntryNumber < 2` argument, consistent with dot/dotdot behavior.

## Output Buffer Formatting

For each match, `UDFFileDirInfoToNT` creates a temporary `FILE_BOTH_DIR_INFORMATION` representation. The routine copies the fixed base fields needed by the requested information class into the caller buffer, copies the Unicode file name bytes, sets `FileIndex`, `FileNameLength`, `NextEntryOffset`, and tracks `IoStatus.Information`.

If the next entry cannot fit:

- after at least one successful entry, it returns `STATUS_SUCCESS`;
- for the first entry, it returns `STATUS_BUFFER_OVERFLOW` and truncates the filename length to the available space policy used here;
- it decrements `NextMatch` so the oversized entry is not lost on the next call.

When no more matches are found, it returns `STATUS_SUCCESS` if at least one entry was returned, `STATUS_NO_SUCH_FILE` for an empty first query, or `STATUS_NO_MORE_FILES` for later continuation queries.

## Notify Change Flow

`UDFNotifyChangeDirectory` validates that the target is a directory, acquires the FCB main resource shared or posts if it cannot wait, rejects delete-pending directories, extracts the completion filter and tree-watch flag, and calls `FsRtlNotifyFullChangeDirectory` with the VCB notify mutex/list, CCB context, directory name, watch-tree flag, completion filter, and IRP. Successful notify setup returns `STATUS_PENDING` and releases the IRP context without completing the IRP.

## Integration Points

The file depends on:

- UDF directory indexes through `UDFDirIndex`, `PDIR_INDEX_HDR`, and `PDIR_INDEX_ITEM`.
- Name helpers: `UDFIsMatchAllMask`, `FsRtlDoesNameContainWildCards`, `UDFBuildHashEntry`, `UDFCanNameBeA8dot3`, `UDFIsNameInExpression`.
- NT output conversion: `UDFFileDirInfoToNT`.
- FCB/CCB fields initialized by create/open paths.
- FsRtl notification APIs and `UDFNotifyFullReportChange` calls elsewhere that wake queued notifications.

## Notable Risks and Edge Cases

- Search state is stored per CCB, so callers that change masks mid-enumeration reset/replace CCB state.
- The function writes `NextEntryOffset` by storing a `ULONG` at `Buffer + LastOffset`; the first entry writes zero initially and previous entries are patched on later iterations.
- Buffer-overflow handling intentionally rewinds `NextMatch`, but truncating `FileNameBytes` on the first oversized entry may produce partial-name semantics that consumers must tolerate.
- Directory validation depends on both FCB flags and `UDFIsADirectory(DirFileInfo)`.
- Posting nonblocking requests requires locking the caller buffer before worker-thread processing.

## Testing Signals

Useful tests include match-all enumeration, wildcard masks, exact masks with hash prefiltering, case-sensitive versus case-insensitive opens, 8.3-compatible masks, restart scans, index-specified scans, single-entry queries, each supported information class, small output buffers, no-match first/later queries, deleted/internal entry skipping, and notify requests on valid, invalid, and delete-pending directories.
