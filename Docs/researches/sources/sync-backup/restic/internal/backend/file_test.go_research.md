# sources/sync-backup/restic/internal/backend/file_test.go

Purpose: Tests backend handle formatting and validation.

Important APIs and functions: `TestHandleString` covers compact display strings. `TestHandleValid` covers invalid type, missing name, config-file exception, and valid lock handle cases.

Control flow and state: Table-driven tests call `Handle.Valid` and compare errors against expected validity.

Dependencies and integration: Uses `internal/test.Equals` and package-local `Handle`/`FileType` values.

Risks and test signals: Guards the core handle contract used by every backend and wrapper.
