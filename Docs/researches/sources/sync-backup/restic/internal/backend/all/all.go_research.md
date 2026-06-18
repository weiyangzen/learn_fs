# sources/sync-backup/restic/internal/backend/all/all.go

Purpose: Central registration point for all supported repository backend factories.

Important APIs and functions: `Backends()` creates a `location.Registry` and registers Azure, B2, Google Cloud Storage, local, rclone, REST, S3, SFTP, and Swift factories.

Control flow and state: Each call returns a new registry populated in fixed order. No global mutable state is stored in this file.

Dependencies and integration: Depends on backend subpackages and `internal/backend/location`. Higher-level repository location parsing uses this registry to open or create the chosen backend.

Risks and test signals: Adding a backend requires updating this list or the backend will not be available through the aggregate registry. There is no direct test in this subset; coverage is usually through location/backend integration tests elsewhere.
