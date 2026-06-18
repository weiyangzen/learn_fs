# sources/user-network-fs/rclone/backend/drive/drive_internal_test.go

## Purpose
This file supplies unit-style and integration-style internal tests for the Drive backend. It validates helper functions that do not need a live remote, loads deterministic Drive format fixtures, and defines `Fs.InternalTest` so rclone's generic integration suite can run Drive-specific scenarios against a configured `TestDrive:`.

## Important APIs, types, and functions
- `TestDriveScopes` validates default scope expansion, comma trimming, and appfolder detection.
- `TestInternalLoadExampleFormats` reads `test/about.json`, unmarshals export/import formats, and seeds `_exportFormats`/`_importFormats` with `fixMimeTypeMap`.
- `TestInternalParseExtensions`, `TestInternalFindExportFormat`, `TestMimeTypesToExtension`, `TestExtensionToMimeType`, `TestExtensionsForExportFormats`, and skipped `TestExtensionsForImportFormats` verify MIME/extension mapping and Google Docs export selection.
- Methods on `*Fs` such as `InternalTestShouldRetry`, `InternalTestDocumentImport`, `InternalTestDocumentUpdate`, `InternalTestDocumentExport`, `InternalTestDocumentLink`, `InternalTestShortcuts`, `InternalTestUnTrash`, `InternalTestCopyOrMoveID`, `InternalTestQuery`, `InternalTestAgeQuery`, `InternalTestSingleQuoteFolder`, and `InternalTestMoveDuplicateParent` are picked up through `fstests.InternalTester`.
- `InternalTest` orders these tests, including nested document import/update/export/link tests that depend on prior remote state.

## Control flow
Pure tests run directly under `go test` and set global format caches where needed. Live remote tests operate through an initialized `*Fs`: they create/copy test files from local fixtures, call backend object methods and backend commands, then assert behavior through rclone listing/check helpers or direct Drive API reads. The document tests are nested because each step depends on the documents created or updated by the previous step.

## State and persistence behavior
The tests mutate the configured Drive remote: they upload sample documents, create and remove shortcuts, create trash/untrash trees, issue copy/move-by-ID operations into temporary local directories, create special-name folders, and create duplicate Drive folders directly through the API. Cleanup is explicit with `Remove`, `Rmdir`, `Purge`, direct `delete`, and `DirCacheFlush` in duplicate-parent scenarios. The file also mutates global `_exportFormats` and `_importFormats` once for deterministic MIME behavior.

## Dependencies and integration points
The tests depend on rclone's local backend, `fs`, `filter`, `operations`, `sync`, `fstest`, `fstests`, random content generation, testify assertions, and Google Drive API structs/errors. They are tightly coupled to behavior in `drive.go`, `metadata.go`, and `upload.go` because they exercise upload conversion, object export, command dispatch, query construction, shortcut resolution, and retry classification.

## Risks and edge cases
- Tests that use a live Drive remote depend on credentials, remote state, API quota, and Drive eventual consistency.
- `InternalTestDocumentImport` temporarily enables `AllowImportNameChange` and must restore it.
- Query tests escape both single quotes and backslashes, guarding a common Drive search failure mode.
- `InternalTestMoveDuplicateParent` covers a subtle Shared Drive risk: moving from a duplicate-name folder must remove the object's actual parent, not the parent guessed by directory cache.
- The skipped import-format extension test indicates known incompleteness or instability in import MIME coverage.

## Test signals
This file is itself the test signal for many Drive backend invariants. It checks retry fatalization for rate/download/upload quota cases, Google Docs import/export/link rendering, shortcut command errors and success paths, trash restore counts, copy/move ID destination naming, filter-aware age queries, single-quote folder listing, and duplicate-parent move correctness.
