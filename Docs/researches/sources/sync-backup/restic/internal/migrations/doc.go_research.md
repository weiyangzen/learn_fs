## sources/sync-backup/restic/internal/migrations/doc.go

Purpose: package documentation for repository/backend migrations.

Important APIs: no executable declarations; it documents that package `migrations` contains migrations applicable to repositories and/or backends.

Control flow and state: none.

Dependencies and integration points: establishes package docs for Go tooling. The actual interfaces and registrations live in neighboring files.

Risks and test signals: minimal; documentation should remain aligned with migration scope if backend-only migrations are added.
