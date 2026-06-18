# sources/sync-backup/kopia/internal/ospath/ospath_test.go

Purpose: portable unit tests for absolute-path detection.

Important APIs/types/functions: `TestIsAbs`.

Control flow: table-driven cases compare `ospath.IsAbs` with expected values for ordinary absolute and relative paths on the current platform.

State and persistence behavior: no state changes.

Dependencies and integration points: validates shared behavior used by config and API path resolution.

Risks and test signals: platform differences limit expectations; Windows-specific edge cases live in a separate test file.
