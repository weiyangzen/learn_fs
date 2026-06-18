# File Research: sources/windows/reactos/drivers/filesystems/cdfs/create.c

## Purpose
Implements the CDFS create/open path for ReactOS, including volume opens, name opens, relative opens, file-ID opens, directory traversal, FCB creation/lookup, share-access checks, oplock handling, and CCB/file-object finalization.

## Key Elements
- `CdCommonCreate` is the main create dispatcher. It rejects unsupported create modes for this read-only filesystem, normalizes names, acquires the VCB, verifies media state, handles volume and file-ID opens specially, searches prefix/path-table state, scans directories for file entries, and completes opens through helper routines.
- `CdNormalizeFileNames` builds the full file-object name from absolute or related-file-object names, strips acceptable trailing separators, rejects malformed double-leading slashes, handles retry state through `IRP_CONTEXT_FLAG_FULL_NAME`, validates 64-bit file IDs, upcases remaining parse names for case-insensitive opens, and rejects wildcards in create names.
- `CdOpenByFileId` decodes CDFS file IDs into path-table and dirent offsets, validates directory/file type, reconstructs missing parent and child FCBs through path-table or directory scans, and then completes the open as a by-ID handle.
- `CdOpenExistingFcb` validates desired access on an already known FCB, derives CCB flags from case-sensitivity and related-open state, then delegates to `CdCompleteFcbOpen`.
- `CdOpenDirectoryFromPathEntry` opens or creates directory index FCBs from path-table entries, inserts exact/case-folded names into the prefix table, optionally performs the user open, and carefully transitions from parent to child FCB locks.
- `CdOpenFileFromFileContext` creates or finds data FCBs from directory enumeration context, inserts long-name or generated short-name prefixes where valid, preserves version/open-by-ID flags, and completes user file opens.
- `CdCompleteFcbOpen` centralizes final open work: expands `MAXIMUM_ALLOWED`, supports exclusive volume lock opens, purges before locking volumes, checks batch/exclusive oplocks, applies share-access rules, creates the CCB, sets file-object type/cache flags, updates cleanup/reference counts, records volume lock state, computes fast-I/O possibility, sets `IoStatus.Information`, and attaches section-object pointers.

## Dependencies
Depends on the CDFS internal object model from `cdprocs.h`: IRP contexts, VCB/FCB/CCB structures, prefix table helpers, path-table and dirent lookup helpers, FCB table creation/lookup, allocation-name conversion, share access, oplock callbacks, teardown/close paths, and Windows kernel I/O primitives such as file-object names, VPB pointers, `IoCheckShareAccess`, and FsRtl oplock APIs.

## Behavior/Risks
- The filesystem is read-only from the create path's point of view: file creation, overwrite-like creation, paging-file opens, target-directory opens, EA creates, and most non-`FILE_OPEN` dispositions are rejected with access or parameter errors.
- Relative opens are accepted only from user file objects with compatible related-open types; related opens through by-ID handles are marked in CCB flags so later code can preserve name semantics.
- Directory opens are accelerated through path-table lookup, while file opens that are not already in the prefix/FCB table fall back to directory scans.
- File-ID validation is defensive: offsets must lie inside the path table or directory stream, directory IDs must point to self entries, and mismatched `FILE_DIRECTORY_FILE`/`FILE_NON_DIRECTORY_FILE` options fail.
- Case-insensitive opens mutate the file object name to the exact on-disk case when a match is found, and prefix entries may be inserted in both exact and upcased forms.
- The locking order is subtle: VCB locks protect FCB-table work, FCB resources protect current traversal nodes, and several paths temporarily reference FCBs while dropping locks to avoid blocking under the VCB lock.
- Oplock paths can return `STATUS_PENDING` after handing ownership to the oplock package, so callers must not assume the IRP or context remains completable in the normal path.
