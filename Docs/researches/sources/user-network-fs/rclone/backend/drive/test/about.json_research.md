# sources/user-network-fs/rclone/backend/drive/test/about.json

## Purpose
`about.json` is a deterministic fixture containing a sample Google Drive About response subset for `importFormats` and `exportFormats`. It lets Drive internal tests exercise MIME conversion logic without requiring a live About API call.

## Important data
- `importFormats` maps ordinary MIME types such as text, CSV, PDF, images, OpenDocument, Microsoft Office, JSON, and script text variants to Google Apps MIME targets such as document, spreadsheet, presentation, drawing, and script.
- `exportFormats` maps Google Apps document, spreadsheet, jam, script, presentation, form, and drawing MIME types to exportable MIME outputs such as PDF, Office formats, OpenDocument formats, plain text, HTML, ZIP, JSON, SVG, PNG, and JPEG.

## Control flow
`TestInternalLoadExampleFormats` reads this JSON file, unmarshals the maps, runs them through `fixMimeTypeMap`, and stores them in package globals `_exportFormats` and `_importFormats`. Later tests use these globals through `findExportFormat`, `findImportFormat`, and extension validation helpers.

## State and persistence behavior
The file is static test data. It does not persist runtime state, but loading it mutates package-level format caches for the duration of the test process.

## Dependencies and integration points
It is consumed by `drive_internal_test.go`. Its MIME values must align with extension registrations in `drive.go`; otherwise tests such as `TestExtensionsForExportFormats` or document import/export tests can fail.

## Risks and edge cases
- Fixture drift from current Google Drive capabilities may hide production behavior changes.
- Some duplicate/legacy MIME types are intentionally represented, relying on Drive backend custom MIME extension registrations.
- Import format validation is partially skipped in tests, so this fixture's import side is less strongly enforced than export side.

## Test signals
The fixture supports deterministic tests for export format choice, MIME extension mappings, and document import/export behavior. It is not executable by itself but is essential to avoiding network-dependent About format tests.
