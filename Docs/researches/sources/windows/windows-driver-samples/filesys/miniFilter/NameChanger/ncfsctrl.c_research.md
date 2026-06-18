# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncfsctrl.c

## Purpose

`ncfsctrl.c` handles user-visible filesystem control results that expose paths or file names. Its job is to preserve the NameChanger illusion: when lower filesystem FSCTLs return paths under the real mapping, this file rewrites, filters, or injects records so callers see the configured user mapping.

## Main Areas

- `NcStreamHandleContextFindBySidCreate` / `NcStreamHandleContextFindBySidClose` initialize and tear down the `FSCTL_FIND_FILES_BY_SID` state embedded in each stream-handle context.
- `NcFindFilesBySidTranslateBuffers` rewrites `FILE_NAME_INFORMATION` records from filesystem-relative names to user-relative names. It builds full names from the opened/query root, compares against the real mapping, optionally constructs user-mapping replacements, suppresses real-mapping entries when required, and tracks partial input/output consumption.
- `NcPreFindFilesBySid` decides whether `FSCTL_FIND_FILES_BY_SID` needs filtering, translation, or injected enumeration from the real mapping. It attaches/locks stream-handle context state, drains buffered leftovers, may retarget the request to the real mapping file object, and completes early for buffer or context errors.
- `NcPostFindFilesBySid` copies volatile METHOD_NEITHER output into a stable system buffer, translates returned records, buffers overflow remnants, and when needed opens the real mapping directory to inject additional results via `FltFsControlFile`.
- `NcPostLookupStreamFromCluster` rewrites Win7+ `LOOKUP_STREAM_FROM_CLUSTER_OUTPUT` entries. It translates absolute real-mapping paths to user-mapping paths, preserves match counts, recomputes required buffer size, and may return fewer records if names grow.
- `NcUsnTranslateBuffers` rewrites USN v2.0 records whose parent file reference and final component identify the real mapping. It changes the parent ID to the user mapping parent ID and substitutes the user mapping link name.
- `NcPostReadFileUsnData`, `NcPostEnumUsnData`, `NcPostReadUsnJournalWorker`, and `NcPostReadUsnJournal` apply USN translation to `FSCTL_READ_FILE_USN_DATA`, `FSCTL_ENUM_USN_DATA`, and `FSCTL_READ_USN_JOURNAL`. They open/query both mapping parents for `FileInternalInformation`, copy user buffers into stable storage, then rewrite records after the leading `USN` cursor where applicable.

## Integration

The file is called from the central FSCTL callbacks in `nc.c`. It depends on mapping/path helpers from `ncmapping.c` and `ncpath.c`, generic helpers from `nchelper.c`, and stream-handle context locking/attachment from `nccontext.c`. It uses Filter Manager primitives (`FltGetInstanceContext`, `FltLockUserBuffer`, `FltFsControlFile`, `FltQueueGenericWorkItem`) and kernel object lifetime management (`FltClose`, `ObDereferenceObject`).

## Important Safety Behavior

- Treats METHOD_NEITHER output as volatile and untrusted; it probes, locks MDLs when present, catches access exceptions, and copies filesystem output before parsing.
- Uses safe integer arithmetic before walking variable-length buffers.
- Defers `FSCTL_READ_USN_JOURNAL` post-processing to a generic work item to avoid reentering the filesystem while top-level IRP/filesystem locks may still be held.
- Only understands USN records with major version 2 and minor version 0; incompatible versions return `STATUS_NOT_IMPLEMENTED`.
- Complexity risk is high around concurrent `FSCTL_FIND_FILES_BY_SID` requests sharing one handle: leftover buffers, real mapping handles, and outstanding request counts must remain synchronized under the stream-handle lock.
