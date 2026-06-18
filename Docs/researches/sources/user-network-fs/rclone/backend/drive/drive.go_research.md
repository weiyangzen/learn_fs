# sources/user-network-fs/rclone/backend/drive/drive.go

## Purpose
`drive.go` is the main rclone backend implementation for Google Drive. It registers the `drive` remote, defines configuration, constructs authenticated Drive clients, maps Drive files/folders/docs/shortcuts into rclone `fs.Fs`, `fs.Object`, and `fs.Directory` interfaces, and implements listing, upload/update, server-side copy/move, trash cleanup, change notification, metadata-aware operations, and backend commands.

## Important APIs, types, and functions
- `Options` is the complete config surface: OAuth scopes, service account/env auth, Shared Drive root selection, listing filters, Google Docs import/export settings, upload cutoffs/chunk sizes, v2 download threshold, retry/pacer controls, shortcut behavior, metadata read/write modes, encoding, and resource keys.
- `Fs` holds runtime state: Drive v3/v2 services, OAuth HTTP client, directory cache, root folder ID, pacer, export/import format caches, ListR grouping state, resource-key cache, and permission cache.
- `baseObject`, `Object`, `documentObject`, `linkObject`, and `Directory` model regular binary objects, exported Google Docs, synthetic link files for Docs, and folders.
- `init` registers the backend and its config wizard, metadata help, OAuth options, and all advanced Drive options. It also registers MIME extension mappings used by Google Docs export/import logic.
- `NewFs`/`newFs` parse config, validate upload knobs, create OAuth/service-account clients, initialize Drive services and feature flags, resolve root folder IDs, initialize `dircache`, parse import/export extensions, and detect whether the requested root is a file.
- `list`, `ListP`, and `ListR` build Drive query expressions and convert Drive API `File` records into rclone entries. `ListR` runs worker goroutines and batches multiple parent IDs, with a fallback for a known Drive grouped-query empty-result bug.
- `NewObject`, `getRemoteInfoWithExport`, `newObjectWithInfo`, `newRegularObject`, `newDocumentObject`, and `newLinkObject` resolve one remote path and build the correct object wrapper, including Google Docs export naming and shortcut dereferencing.
- `Put`, `PutUnchecked`, `Object.Update`, `documentObject.Update`, `Copy`, `Move`, `DirMove`, `MkdirMetadata`, `DirSetModTime`, `Purge`, `CleanUp`, `PublicLink`, `ChangeNotify`, and `Command` implement the backend's rclone optional interfaces.
- Shortcut helpers `joinID`, `splitID`, `actualID`, `shortcutID`, and `resolveShortcut` preserve both the target Drive ID and shortcut file ID so callers can intentionally act on the underlying object or the shortcut placeholder.

## Control flow
Backend construction starts in `NewFs`: configuration is parsed, root ID is chosen from explicit root, team drive, or Drive root lookup, `dircache` maps paths to IDs, export/import formats are prepared, then `FindRoot` determines whether the remote path is a directory or a file parent. Listing is query driven: `list` assembles filters for trash state, parent IDs, shared-with-me/starred roots, case-sensitive title validation, Google Docs export stems, directory/file filters, optional age filters, Shared Drive corpora, appDataFolder spaces, resource-key headers, and paginated fields. Each returned item is name-decoded, shortcut-resolved when enabled, filtered again for exact title/export name, then passed to a callback.

Object creation branches on Drive MIME/checksum state. Regular uploaded files have hashes and media download URLs. Google Docs are represented either as exported document objects with an added extension and unknown size, or as synthetic link objects generated from templates. Unknown or unexportable Docs are hidden unless `--drive-show-all-gdocs` allows them. Dangling shortcuts can be exposed as unreadable regular-looking objects when not skipped so users can delete them.

Uploads use regular Drive create/update for objects below `UploadCutoff`, and the custom resumable uploader in `upload.go` for larger or unknown-size data. Importable local files can be converted to Google Docs by matching source MIME type against configured import formats, stripping the export extension from the Drive name, and validating that the chosen export type does not silently change unless allowed. Metadata is merged before upload/update and finalized afterward through callbacks for owner, permissions, and labels.

Server-side copy/move uses Drive `Files.Copy` or `Files.Update` with add/remove parents. Copy may copy shortcut content or shortcut files depending on config, preserves Doc descriptions specially, and deletes an existing destination object after successful copy. Move chooses the source parent from the object's recorded `parents` when possible, avoiding directory-cache ambiguity when duplicate folder names exist. Folder moves use `dircache.DirMove` plus a Drive update. Trash and cleanup code chooses between setting `Trashed` and hard delete based on config and context.

## State and persistence behavior
Persistent remote state lives in Google Drive files, folders, permissions, labels, trash state, and revisions. Local runtime state includes `dirCache`, `dirResourceKeys`, permission cache, ListR grouping/empty-directory state, and cached global export/import format maps guarded by `sync.Once`. Config updates through the `set` backend command mutate both the in-memory `Options` and the config mapper for chunk size/service account file. Object metadata is cached in `baseObject.metadata` when fetched or parsed; `Metadata` lazily reloads from Drive when absent.

Drive ID state is nuanced: shortcut-resolved IDs can be composite `actualID<TAB>shortcutID`. APIs that need the real content ID call `actualID`; APIs that should operate on the visible shortcut file call `shortcutID`. Resource keys for link-shared folders are cached by directory ID and injected into list/download/copy headers.

## Dependencies and integration points
This file integrates heavily with rclone core packages: `fs` optional interfaces, `dircache`, `pacer`, `oauthutil`, `fshttp`, `filter`, `operations`, `cache`, `fspath`, metadata helpers, hash sets, and encoders. External dependencies are Google Drive v3/v2 clients, Google OAuth/JWT/default credentials, and Google API error/field helpers. It calls into sibling files for metadata handling (`systemMetadataInfo`, `metadataFields`, `fetchAndUpdateMetadata`) and resumable upload (`Fs.Upload`). Tests in `drive_test.go` and `drive_internal_test.go` exercise the exported optional interfaces and internal backend commands.

## Risks and edge cases
- Google Drive allows duplicate names, multiple parents, shortcuts, Shared Drive inheritance, resource keys, and eventual consistency; many operations rely on careful ID/parent handling.
- Query escaping for names with backslashes and quotes is critical and is covered by internal tests.
- `shouldRetry` contains string/reason based fatal handling for upload/download quotas, which is necessarily brittle against undocumented Google error changes.
- ListR batching includes a workaround that disables grouping on suspicious empty results; concurrency around channels, wait groups, and overflow must remain correct to avoid missed directories or deadlocks.
- Updating Google Docs requires import formats and refuses type changes; link objects cannot be updated.
- Deleting objects with multiple parents is refused for safety.
- Metadata owner/permission/label writes happen after upload and may partially fail depending on `failok` flags.
- Some operations use sleeps/workarounds for Drive bugs, such as setting copied Google Doc modtimes after a delay.

## Test signals
`drive_test.go` runs full rclone integration tests against `TestDrive:` and advertises upload chunk/cutoff setters. `drive_internal_test.go` adds targeted tests for scopes, MIME extension mappings, export/import formats, retry policy, document import/update/export/link behavior, shortcut creation, untrash, copy/move by ID, query escaping, age-filter query integration, single-quote folders, and duplicate-parent move behavior. The mocked `test/about.json` supplies deterministic import/export format data for internal tests.
