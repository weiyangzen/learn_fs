# sources/sync-backup/restic/internal/filter/include_test.go

Purpose: Unit tests for include matcher behavior.

Important APIs: `TestIncludeByPattern` and `TestIncludeByInsensitivePattern` instantiate match functions from patterns `*.go` and `README.md`.

Control flow and state: Each table case builds a fresh include function and verifies only the `matched` result. `childMayMatch` is intentionally ignored here.

Dependencies and integration: Uses Go `testing` and the filter package directly. It validates behavior expected by CLI include options without involving command parsing.

Risks: Does not cover `CollectPatterns`, include-file reading, validation failures, warning callbacks, malformed patterns, or child traversal hints.

Test signals: The file itself is the primary signal: it confirms basename-oriented glob behavior and lowercased matching for uppercase file names.
