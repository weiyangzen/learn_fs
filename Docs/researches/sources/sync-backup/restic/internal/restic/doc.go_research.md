
# sources/sync-backup/restic/internal/restic/doc.go

Purpose: package documentation for the central `internal/restic` package.

The comment describes this package as containing repository types and functions. There are no APIs or state in this file itself. Its value is organizational: source files in this package define IDs, file/blob types, config, JSON helpers, sets, repository interfaces, and backend listing helpers used by many internal packages.

Risks are documentation drift only. Behavioral test signals live in the sibling files such as ID tests, blob tests, config tests, and backend-find tests.
