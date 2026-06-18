# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/simrep/simrep.c

## Scope And Role

`simrep.c` is a Windows Filter Manager mini-filter sample that demonstrates simulated reparse behavior. It redirects creates from a configured `OldMapping` path to a configured `NewMapping` path by replacing the target `FILE_OBJECT->FileName` and completing the create with `STATUS_REPARSE`.

The file is not a full namespace virtualization layer. Its own header explicitly frames it as a sample for returning `STATUS_REPARSE`; callers and upper filters can still observe the redirected target after create/rename/link completion.

Read coverage: full file, 3,177 lines.

## Main State

The central global is `SIMREP_GLOBAL_DATA Globals`, containing:

- `Filter`: registered `PFLT_FILTER`.
- `Mapping.OldName` and `Mapping.NewName`: registry-driven redirect path pair.
- `ReplaceFileNameFunction`: dynamically resolved `IoReplaceFileObjectName`, or fallback `SimRepReplaceFileObjectName`.
- `QueryDirectoryFileFunction`: dynamically resolved `FltQueryDirectoryFile`, or fallback callback-data implementation.
- `RemapRenamesAndLinks`: registry-controlled option that changes callback registration and enables name-provider behavior.
- `DebugLevel` in DBG builds.

Pool tags are split between string allocations (`SIMREP_STRING_TAG`) and registry value buffers (`SIMREP_REG_TAG`).

## Registration And Initialization

`DriverEntry` initializes pool NX opt-in, default globals, dynamically resolves `IoReplaceFileObjectName` and `FltQueryDirectoryFile`, reads configuration, registers with Filter Manager, and starts filtering.

There are two registration tables:

- `FilterRegistration`: create and network-query-open callbacks only.
- `FilterRegistrationWithRename`: create, network-query-open, set-information callbacks, plus pass-through name-provider callbacks.

`SimRepSetConfiguration` opens the service `Parameters` key using `IoOpenDriverRegistryKey` when available, with a `ZwOpenKey` fallback for older systems. It reads:

- `DebugLevel` in DBG builds.
- `RemapRenamesAndLinks`.
- `OldMapping`.
- `NewMapping`.

It validates that old/new mappings agree on trailing-backslash semantics, preventing a directory mapping from being paired with a file-style mapping or vice versa.

## Create Redirection Flow

`SimRepPreCreate` is the main IRP create path:

1. Ignores paging-file opens, volume opens, and open-by-file-id creates.
2. Avoids `SL_OPEN_TARGET_DIRECTORY` reparsing unless rename/link remapping is enabled.
3. Gets opened name information, using `FLT_FILE_NAME_QUERY_FILESYSTEM_ONLY` for target-directory opens to avoid polluting the name cache.
4. Parses the name.
5. Calls `SimRepMungeName` to replace the old mapping prefix with the new mapping prefix.
6. Replaces the target file object's name through `Globals.ReplaceFileNameFunction`.
7. Completes the operation with `STATUS_REPARSE` and `IO_REPARSE`.

The mapping comparison is prefix-based but path-boundary aware. `SimRepCompareMapping` treats a match as exact if the post-volume path length equals the mapping length, or as a child match if the next character is `\`. This avoids treating `\a\b` as matching `\a\bc`.

## Network Query Open Flow

`SimRepPreNetworkQueryOpen` handles `IRP_MJ_NETWORK_QUERY_OPEN`, which arrives as Fast I/O. Since Fast I/O cannot return `STATUS_REPARSE`, the callback only checks whether the path matches the old mapping. If it does, it returns `FLT_PREOP_DISALLOW_FASTIO`, forcing the I/O manager to reissue the operation as a normal IRP create where `SimRepPreCreate` can return `STATUS_REPARSE`.

It rejects/ignores paging files, volume opens, file-id opens, and asserts target-directory opens should not arrive on this path.

## Rename And Hardlink Remapping

When `RemapRenamesAndLinks` is enabled, `SimRepPreSetInformation` handles:

- `FileRenameInformation`
- `FileRenameInformationEx`
- `FileLinkInformation`

It ignores all other listed information classes and asserts on unknown ones in test builds.

The callback obtains destination name information via `FltGetDestinationFileNameInformation` using `FLT_FILE_NAME_REQUEST_FROM_CURRENT_PROVIDER`, then parses the result. Stream destinations are passed through. For matching destinations, it builds a replacement rename/link information buffer with a munged absolute target path and issues `FltSetInformationFile` itself, then completes the original operation.

A special exact-match fallback handles destinations that overlap the old mapping exactly, because parent-directory name resolution may not reparse in that case.

## Name Provider Support

Rename/link support requires SimRep to participate in name resolution. The file implements a pass-through name provider:

- `SimRepGenerateFileName` clears `FLT_FILE_NAME_REQUEST_FROM_CURRENT_PROVIDER` to avoid recursion, then delegates name retrieval below itself using `FltGetFileNameInformation` or `FltGetFileNameInformationUnsafe`.
- It copies the returned name into the provided `FLT_NAME_CONTROL`.
- It only allows caching once `FileObject->FsContext` is non-NULL.

`SimRepNormalizeNameComponent` and Vista+ `SimRepNormalizeNameComponentEx` open the parent directory, query a single `FileNamesInformation` entry for the component, and return the long/normalized component name. The Vista+ variant propagates transaction context from the target file object through `FltCreateFileEx2`.

`SimRepQueryDirectoryFile` calls `FltQueryDirectoryFile` when exported; otherwise it builds and performs an `IRP_MJ_DIRECTORY_CONTROL / IRP_MN_QUERY_DIRECTORY` callback-data request manually.

## Resource Handling

The file uses explicit allocation/free helpers for `UNICODE_STRING` values. Configuration cleanup frees partially initialized mapping strings on failure. Unload unregisters the filter and frees global mapping strings.

Name/query structures are released with `FltReleaseFileNameInformation`; directory/file objects from normalization are closed/dereferenced on cleanup paths.

The fallback `SimRepReplaceFileObjectName` either reuses the existing file-name buffer if large enough or allocates a new one and replaces the file object's name buffer directly. The header notes this fallback can trigger Driver Verifier pool-leak complaints on systems without `IoReplaceFileObjectName`.

## Important Risks And Edge Cases

- Debug-only null dereference risk: in the `SL_OPEN_TARGET_DIRECTORY` branch of `SimRepPreCreate`, the debug trace references `&nameInfo->Name` immediately after clearing the flag, before `nameInfo` is populated. With the relevant debug trace flag enabled, this can dereference an invalid `UNICODE_STRING`.
- Mapping semantics are intentionally simple and do not account for NT short names.
- The sample does not honor `FILE_OPEN_REPARSE_POINT`; it always treats the configured mapping as filter-owned behavior rather than an object that can itself be opened/deleted.
- Open-by-file-id is skipped because the path intent cannot be inferred.
- Rename/link redirection is only consistent when the filter is registered as a name provider; without `RemapRenamesAndLinks`, target-directory opens are deliberately passed through.
- The fallback manual file-object name replacement is compatibility code with verifier/unload caveats.
- The directory-query fallback manually constructs callback data and depends on synchronous completion semantics.

## Integration Points

This file integrates deeply with Filter Manager and NT kernel APIs:

- Registration/start: `FltRegisterFilter`, `FltStartFiltering`, `FltUnregisterFilter`.
- Name queries: `FltGetFileNameInformation`, `FltParseFileNameInformation`, `FltGetDestinationFileNameInformation`.
- Reparse behavior: target file-object name replacement plus `STATUS_REPARSE` / `IO_REPARSE`.
- Rename/link replay: `FltSetInformationFile`.
- Name provider callbacks for generated and normalized names.
- Registry configuration through `IoOpenDriverRegistryKey` or `ZwOpenKey`.

## Testing Notes

Useful focused tests would cover:

- Create under old mapping returns `STATUS_REPARSE` and targets new mapping.
- Non-matching creates pass through.
- Boundary case `\oldpath2` does not match mapping `\oldpath`.
- Case-sensitive vs case-insensitive opens.
- Fast I/O network query open under old mapping returns `FLT_PREOP_DISALLOW_FASTIO`.
- `SL_OPEN_TARGET_DIRECTORY` behavior with `RemapRenamesAndLinks` both disabled and enabled.
- Rename/link destination remapping for old mapping exact match, child match, new mapping overlap, stream names, and non-matching destinations.
- Downlevel behavior where `IoReplaceFileObjectName` or `FltQueryDirectoryFile` is unavailable.
