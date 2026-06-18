# sources/sync-backup/restic/cmd/restic/cmd_backup_test.go

Purpose: focused unit tests for backup target collection and raw filename parsing.

Important tests: `TestCollectTargets` creates files and verifies that `--files-from` trims/comments/globs, `--files-from-verbatim` preserves literal names including spaces/special chars, `--files-from-raw` reads NUL-separated names, command-line args merge with file inputs, and missing sources return `ErrInvalidSourceData`. `TestReadFilenamesRaw` validates exact byte preservation for raw names, empty input, empty filename rejection, and missing trailing NUL rejection.

State/persistence: creates temporary files only. It does not open a repository.

Dependencies/integration: uses `rtest.TempDir`, OS filesystem operations, and `collectTargets`/`readFilenamesRaw` from `cmd_backup.go`.

Risks/test signals: this directly protects user-facing edge cases around filenames that contain whitespace, glob characters, invalid UTF-8, and embedded newlines. It does not cover full archiver behavior; integration tests do that.
