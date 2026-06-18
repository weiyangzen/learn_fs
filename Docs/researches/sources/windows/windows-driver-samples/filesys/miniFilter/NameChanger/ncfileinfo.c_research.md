# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncfileinfo.c

## Scope

This file implements NameChanger handling for query-file-information and set-file-information operations whose payloads contain paths, link names, short names, delete disposition, or rename targets. Its purpose is to keep returned names user-visible and to prevent operations that would expose, overwrite, delete, rename, or destabilize the hidden real mapping and the visible user mapping.

## APIs and Entry Points

- `NcPostQueryName` rewrites returned `FileNameInformation`, `FileNormalizedNameInformation`, and `FileAllInformation` names from real mapping paths to user mapping paths.
- `NcPreQueryAlternateName` intercepts alternate-name queries for the mapping itself and returns the user mapping short final component.
- `NcPostQueryHardLinks` rewrites hard-link entries that refer to the real mapping link so they appear under the user mapping parent and name.
- `NcPreSetShortName` blocks short-name changes that target the mapping, mapping ancestors, or names reserved by the user mapping.
- `NcPreSetDisposition` blocks delete disposition on ancestors of either mapping.
- `NcPreSetLinkInformation` redirects hard-link creation inside the user mapping to the corresponding real mapping path and blocks links into the hidden real mapping.
- `NcPreRename` validates source and target overlap, blocks unsafe ancestor or hidden-real operations, and redirects renames into the user mapping to the real mapping path.

## Control Flow

`NcPostQueryName` runs after successful name queries, or after `STATUS_BUFFER_OVERFLOW`. It gets the instance mapping, finds the returned name inside the user buffer, checks overlap with the real mapping, adjusts `FileNameLength` and `IoStatus.Information`, then copies the user mapping path and optional remainder into the caller's buffer. On buffer overflow it biases the required name length when the user mapping is longer than the real mapping.

`NcPreQueryAlternateName` gets the opened name and only handles the mapping object itself. Non-mapping objects pass through. For the mapping, it returns `UserMapping.ShortNamePath.FinalComponentName` directly if the caller's buffer is large enough.

`NcPostQueryHardLinks` takes a copy of the filesystem's `FILE_LINKS_INFORMATION` result, opens both real and user mapping parent directories, queries their file IDs, then walks each link entry. Entries whose parent ID and final component match the real mapping long or short final component are rewritten to the user mapping parent ID and long final component.

`NcPreSetShortName` skips filesystems without short names, then denies short-name changes on the mapping, either mapping's ancestors, invalid oversized names, or peer names that collide with the user mapping long or short final component. Other requests pass through.

`NcPreSetDisposition` ignores attempts to clear delete disposition. For delete requests, it gets the opened name and denies deletion of ancestors of either the real or user mapping.

`NcPreSetLinkInformation` resolves the destination with `FltGetDestinationFileNameInformation`. It denies linking to the real mapping itself, rejects unexpected links inside the real mapping, denies replace-over-existing on mapping ancestors, passes through destinations outside the user mapping, and redirects destinations inside the user mapping by constructing the equivalent real mapping name and issuing `FltSetInformationFile` itself.

`NcPreRename` validates both source and target. It denies renaming an ancestor of either mapping, denies targets inside the real mapping, denies replace-over-existing on mapping ancestors, passes through targets outside the user mapping, and redirects non-stream renames into the user mapping by issuing a new rename request to the corresponding real mapping target.

## State and Data Flow

The file uses `PNC_INSTANCE_CONTEXT->Mapping`, especially:

- `UserMapping.LongNamePath.VolumelessName`
- `UserMapping.LongNamePath.ParentPath`
- `UserMapping.LongNamePath.FinalComponentName`
- `UserMapping.ShortNamePath.FinalComponentName`
- `RealMapping.LongNamePath.VolumelessName`
- `RealMapping.LongNamePath.ParentPath`
- `RealMapping.LongNamePath.FinalComponentName`
- `RealMapping.ShortNamePath.FinalComponentName`

Path comparisons use `NcComparePath` to obtain `Match`, `InMapping`, `Ancestor`, `Parent`, `Peer`, and remainder information. Redirection uses `NcConstructPath` to combine a target remainder under the real mapping.

For redirected link and rename operations, the file allocates a fresh `FILE_LINK_INFORMATION` or `FILE_RENAME_INFORMATION`, sets `RootDirectory = NULL`, copies the constructed full target path, issues `FltSetInformationFile`, and completes the original callback data without passing the original operation down.

## Dependencies

- Includes `nc.h` and uses shared NameChanger helpers for mapping comparison, path construction, name query, file open, and exception cleanup.
- Uses Filter Manager APIs: `FltGetInstanceContext`, `FltReleaseContext`, `FltGetDestinationFileNameInformation`, `FltParseFileNameInformation`, `FltReleaseFileNameInformation`, `FltQueryInformationFile`, `FltSetInformationFile`, and `FltClose`.
- Uses `NcCreateFileHelper` to open mapping parent directories while ignoring share access checks where required.
- Uses Windows file information structures: `FILE_NAME_INFORMATION`, `FILE_ALL_INFORMATION`, `FILE_LINKS_INFORMATION`, `FILE_LINK_ENTRY_INFORMATION`, `FILE_LINK_INFORMATION`, `FILE_RENAME_INFORMATION`, `FILE_DISPOSITION_INFORMATION`, and `FILE_DISPOSITION_INFORMATION_EX`.
- Uses allocation tags `NC_TAG`, `NC_SET_LINK_BUFFER_TAG`, and `NC_RENAME_BUFFER_TAG`.

## Risks and Edge Cases

- `NcPostQueryName` must preserve Windows name-query overflow semantics: `STATUS_BUFFER_OVERFLOW` is not success, but `IoStatus.Information` still reports copied bytes and `FileNameLength` reports the needed name length.
- Hard-link enumeration can report an inaccurate required size on an initial filesystem overflow because the filter cannot transform a full result it does not yet have; the comments explicitly accept a second-call correction.
- Hard-link rewriting depends on parent file IDs plus final component comparison. If parent ID queries fail, the operation fails rather than returning partially transformed data.
- Alternate-name behavior intentionally differs from NTFS for open-by-ID and potential multiple alternate names.
- Short-name setting is denied for mapping-sensitive cases because the mapping's long/short name pairings are treated as read-only.
- Rename and link redirection cannot safely mutate the original callback buffer because filesystems may use target-directory state from earlier `OPEN_TARGET_DIRECTORY` processing; the file issues its own operation instead.
- Stream rename targets beginning with `:` are passed through even if the containing path overlaps the user mapping, because only the stream name changes.
- The code handles `FileRenameInformationEx` and `FileDispositionInformationEx` flag forms as well as older boolean fields.

## Research Notes

This file enforces NameChanger's metadata invariants for user-visible file information. Query paths are rewritten from real to user view; mutation paths are either denied when they would damage mapping structure or redirected from user mapping targets to the real backing path.
