# sources/storage-engines/pebble/internal/manifest/scan_cursor_test.go

## Purpose
This datadriven test validates `ScanCursor` traversal across manifest versions and external virtual table detection. It verifies cursor stability and advancement semantics.

## Important APIs And Helpers
- `mockExternalObjProvider` implements `objstorage.Provider.Lookup` and marks disk file numbers at or above a threshold as external.
- `TestScanCursor` supports datadriven `define` and `cursor` commands.
- Cursor script commands include `start`, `next-external-file`, and `iterate-external-files`.

## Control Flow
`define` parses a debug version and initializes L0 sublevels. `cursor` creates user-key bounds, initializes the cursor, repeatedly calls `NextExternalFile`, and advances with `MakeScanCursorAfterFile`. The test deliberately calls `NextExternalFile` twice before advancing to ensure the cursor still points to the same file.

## State And Persistence Behavior
The test uses debug-version parsing, not actual manifest record replay. It models external object state through a deterministic object provider threshold.

## Dependencies And Integration Points
It integrates `ParseVersionDebug`, `L0Organizer`, `ScanCursor`, `objstorage` metadata, `base.UserKeyBounds`, and datadriven fixture `testdata/scan_cursor`.

## Risks And Test Signals
The test catches regressions in cursor advancement, external filtering, and L0/L1+ scan ordering. It does not cover object provider errors because the mock lookup always succeeds.
