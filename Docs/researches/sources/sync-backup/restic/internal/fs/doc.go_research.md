# sources/sync-backup/restic/internal/fs/doc.go

Purpose: Package documentation for `internal/fs`.

Important APIs: Declares package `fs` and describes it as an OS-independent filesystem abstraction suitable for backup.

Control flow and state: None.

Dependencies and integration: The doc anchors a package that wraps local OS files, synthetic reader-backed filesystems, metadata conversion, restore creation, and platform-specific file attributes.

Risks: Documentation is intentionally broad; behavior details live in interfaces and platform files.

Test signals: No direct tests; package-level behavior is heavily covered by `fs_*`, `node_*`, and platform tests.
