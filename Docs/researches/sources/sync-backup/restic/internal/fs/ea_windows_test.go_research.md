# sources/sync-backup/restic/internal/fs/ea_windows_test.go

Purpose: Windows-only tests for extended attribute serialization and NT EA operations.

Important APIs: `TestRoundTripEas`, `TestEasDontNeedPaddingAtEnd`, `TestTruncatedEasFailCorrectly`, `TestNilEasEncodeAndDecodeAsNil`, `TestSetFileEa`, `TestSetGetFileEA`, `TestSetGetFolderEA`, and `TestPathSupportsExtendedAttributes`.

Control flow and state: Tests use generated random EA values, temporary files/folders, explicit Windows handles with read/write EA rights, and cleanup helpers that close both Go files and Windows handles.

Dependencies and integration: Validates `ea_windows.go` and the `go-winio` layout against `NtSetEaFile` and `NtQueryEaFile`. Supports higher-level xattr restore tests.

Risks: Assumes the system drive supports EAs and that invalid `Z:` paths fail. Random EA value lengths avoid zero but can make failures less reproducible beyond the generated content.

Test signals: Provides strong Windows-specific confidence for EA binary layout, handle access flags, directory EA handling, and unsupported-path errors.
